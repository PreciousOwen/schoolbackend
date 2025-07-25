# reservations/services.py

from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta, time
from typing import List, Dict, Optional, Tuple

from .models import Table, Reservation, ReservationAvailability, ReservationWaitlist


class ReservationService:
    """Service for managing reservations and availability"""
    
    @staticmethod
    def check_availability(date: datetime.date, start_time: time, 
                          duration_minutes: int, party_size: int,
                          table_id: Optional[int] = None) -> Dict:
        """Check table availability for given parameters"""
        
        # Convert to datetime objects
        start_datetime = datetime.combine(date, start_time)
        end_datetime = start_datetime + timedelta(minutes=duration_minutes)
        
        # Get tables that can accommodate party size
        suitable_tables = Table.objects.filter(seats__gte=party_size)
        if table_id:
            suitable_tables = suitable_tables.filter(id=table_id)
        
        available_tables = []
        unavailable_tables = []
        
        for table in suitable_tables:
            is_available = ReservationService._is_table_available(
                table, start_datetime, end_datetime
            )
            
            table_info = {
                'table_id': table.id,
                'table_number': table.number,
                'seats': table.seats,
                'description': table.description
            }
            
            if is_available:
                available_tables.append(table_info)
            else:
                # Find next available slot
                next_slot = ReservationService._find_next_available_slot(
                    table, start_datetime, duration_minutes
                )
                table_info['next_available'] = next_slot
                unavailable_tables.append(table_info)
        
        return {
            'requested_datetime': start_datetime.isoformat(),
            'duration_minutes': duration_minutes,
            'party_size': party_size,
            'available_tables': available_tables,
            'unavailable_tables': unavailable_tables,
            'total_available': len(available_tables),
            'alternative_suggestions': ReservationService._get_alternative_suggestions(
                date, start_time, duration_minutes, party_size
            ) if not available_tables else []
        }
    
    @staticmethod
    def _is_table_available(table: Table, start_datetime: datetime, 
                           end_datetime: datetime) -> bool:
        """Check if a specific table is available for the time period"""
        
        # Check for existing reservations
        conflicting_reservations = Reservation.objects.filter(
            table=table,
            status__in=[Reservation.PENDING, Reservation.CONFIRMED],
            start_time__lt=end_datetime,
            end_time__gt=start_datetime
        )
        
        if conflicting_reservations.exists():
            return False
        
        # Check availability patterns (if configured)
        day_of_week = start_datetime.weekday()
        availability_patterns = ReservationAvailability.objects.filter(
            table=table,
            day_of_week=day_of_week,
            start_time__lte=start_datetime.time(),
            end_time__gte=end_datetime.time(),
            is_available=True
        )
        
        # If patterns exist, at least one must match
        if ReservationAvailability.objects.filter(table=table).exists():
            return availability_patterns.exists()
        
        # If no patterns configured, assume available during business hours
        business_start = time(11, 0)  # 11 AM
        business_end = time(22, 0)    # 10 PM
        
        return (business_start <= start_datetime.time() <= business_end and
                business_start <= end_datetime.time() <= business_end)
    
    @staticmethod
    def _find_next_available_slot(table: Table, requested_datetime: datetime,
                                 duration_minutes: int) -> Optional[str]:
        """Find the next available slot for a table"""
        
        # Look for slots in the next 7 days
        for days_ahead in range(7):
            check_date = requested_datetime.date() + timedelta(days=days_ahead)
            
            # Check every 30-minute slot during business hours
            for hour in range(11, 22):  # 11 AM to 10 PM
                for minute in [0, 30]:
                    slot_time = time(hour, minute)
                    slot_datetime = datetime.combine(check_date, slot_time)
                    
                    if slot_datetime <= requested_datetime:
                        continue
                    
                    end_datetime = slot_datetime + timedelta(minutes=duration_minutes)
                    
                    if ReservationService._is_table_available(table, slot_datetime, end_datetime):
                        return slot_datetime.isoformat()
        
        return None
    
    @staticmethod
    def _get_alternative_suggestions(date: datetime.date, start_time: time,
                                   duration_minutes: int, party_size: int) -> List[Dict]:
        """Get alternative time suggestions when no tables are available"""
        
        suggestions = []
        
        # Try different times on the same day
        for hour_offset in [-2, -1, 1, 2]:
            alt_time = (datetime.combine(date, start_time) + 
                       timedelta(hours=hour_offset)).time()
            
            if time(11, 0) <= alt_time <= time(20, 0):  # Within business hours
                availability = ReservationService.check_availability(
                    date, alt_time, duration_minutes, party_size
                )
                
                if availability['total_available'] > 0:
                    suggestions.append({
                        'date': date.isoformat(),
                        'time': alt_time.isoformat(),
                        'available_tables': availability['total_available']
                    })
        
        # Try same time on different days
        for days_ahead in range(1, 8):
            alt_date = date + timedelta(days=days_ahead)
            availability = ReservationService.check_availability(
                alt_date, start_time, duration_minutes, party_size
            )
            
            if availability['total_available'] > 0:
                suggestions.append({
                    'date': alt_date.isoformat(),
                    'time': start_time.isoformat(),
                    'available_tables': availability['total_available']
                })
        
        return suggestions[:5]  # Return top 5 suggestions
    
    @staticmethod
    def create_reservation(customer, table_id: int, start_datetime: datetime,
                          end_datetime: datetime, party_size: int,
                          special_requests: str = '') -> Tuple[bool, str, Optional[Reservation]]:
        """Create a reservation with validation"""
        
        try:
            table = Table.objects.get(id=table_id)
        except Table.DoesNotExist:
            return False, "Table not found", None
        
        # Double-check availability
        if not ReservationService._is_table_available(table, start_datetime, end_datetime):
            return False, "Table is no longer available", None
        
        # Create reservation
        reservation = Reservation.objects.create(
            customer=customer,
            table=table,
            party_size=party_size,
            start_time=start_datetime,
            end_time=end_datetime,
            status=Reservation.PENDING
        )
        
        # Check waitlist for notifications
        ReservationService._process_waitlist_notifications(table, start_datetime.date())
        
        return True, "Reservation created successfully", reservation
    
    @staticmethod
    def _process_waitlist_notifications(table: Table, date: datetime.date):
        """Process waitlist and notify customers of availability"""
        
        # Find waitlist entries that might be interested
        waitlist_entries = ReservationWaitlist.objects.filter(
            Q(table_preference=table) | Q(table_preference__isnull=True),
            preferred_date=date,
            is_active=True,
            expires_at__gt=timezone.now()
        ).order_by('created_at')
        
        for entry in waitlist_entries:
            # Check if there's now availability for this customer
            availability = ReservationService.check_availability(
                entry.preferred_date,
                entry.preferred_time,
                120,  # Assume 2-hour duration
                entry.party_size,
                entry.table_preference.id if entry.table_preference else None
            )
            
            if availability['total_available'] > 0:
                # Send notification (this would integrate with the notification service)
                entry.notified_at = timezone.now()
                entry.save()
                
                # You would call NotificationService here
                # NotificationService.send_notification(
                #     user=entry.customer,
                #     event_type='reservation_available',
                #     context_data={'availability': availability}
                # )
    
    @staticmethod
    def add_to_waitlist(customer, preferred_date: datetime.date, 
                       preferred_time: time, party_size: int,
                       table_preference: Optional[Table] = None,
                       flexible_options: Dict = None) -> ReservationWaitlist:
        """Add customer to waitlist"""
        
        flexible_options = flexible_options or {}
        expires_at = timezone.now() + timedelta(
            days=flexible_options.get('max_wait_days', 7)
        )
        
        waitlist_entry = ReservationWaitlist.objects.create(
            customer=customer,
            preferred_date=preferred_date,
            preferred_time=preferred_time,
            party_size=party_size,
            table_preference=table_preference,
            flexible_date=flexible_options.get('flexible_date', False),
            flexible_time=flexible_options.get('flexible_time', False),
            max_wait_days=flexible_options.get('max_wait_days', 7),
            notify_by_email=flexible_options.get('notify_by_email', True),
            notify_by_sms=flexible_options.get('notify_by_sms', False),
            expires_at=expires_at
        )
        
        return waitlist_entry
    
    @staticmethod
    def get_daily_schedule(date: datetime.date) -> Dict:
        """Get the full reservation schedule for a day"""
        
        reservations = Reservation.objects.filter(
            start_time__date=date,
            status__in=[Reservation.PENDING, Reservation.CONFIRMED]
        ).select_related('table', 'customer').order_by('start_time')
        
        schedule = {}
        for reservation in reservations:
            table_key = f"table_{reservation.table.number}"
            if table_key not in schedule:
                schedule[table_key] = {
                    'table_id': reservation.table.id,
                    'table_number': reservation.table.number,
                    'seats': reservation.table.seats,
                    'reservations': []
                }
            
            schedule[table_key]['reservations'].append({
                'id': reservation.id,
                'customer': reservation.customer.username,
                'party_size': reservation.party_size,
                'start_time': reservation.start_time.isoformat(),
                'end_time': reservation.end_time.isoformat(),
                'status': reservation.status,
                'duration_minutes': reservation.duration_minutes
            })
        
        return schedule
