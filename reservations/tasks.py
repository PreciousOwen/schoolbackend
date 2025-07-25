# reservations/tasks.py

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from .models import Reservation, ReservationWaitlist
from .services import ReservationService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_expired_waitlist(self):
    """Process and clean up expired waitlist entries"""
    try:
        now = timezone.now()
        
        # Find expired waitlist entries
        expired_entries = ReservationWaitlist.objects.filter(
            expires_at__lt=now,
            is_active=True
        )
        
        expired_count = expired_entries.count()
        
        # Mark as inactive
        expired_entries.update(is_active=False)
        
        logger.info(f"Processed {expired_count} expired waitlist entries")
        return f"Processed {expired_count} expired waitlist entries"
        
    except Exception as e:
        logger.error(f"Error processing expired waitlist: {e}")
        raise self.retry(countdown=60 * (2 ** self.retries))


@shared_task(bind=True, max_retries=3)
def send_reservation_reminders(self):
    """Send reminders for upcoming reservations"""
    try:
        now = timezone.now()
        
        # Find reservations starting in 2 hours
        reminder_time = now + timedelta(hours=2)
        
        upcoming_reservations = Reservation.objects.filter(
            start_time__gte=now,
            start_time__lte=reminder_time,
            status=Reservation.CONFIRMED
        ).select_related('customer', 'table')
        
        reminder_count = 0
        
        for reservation in upcoming_reservations:
            # Check if reminder already sent (you might want to add a field for this)
            try:
                # Send notification
                from notifications.services import NotificationService
                from notifications.models import NotificationTemplate
                
                NotificationService.send_notification(
                    user=reservation.customer,
                    event_type=NotificationTemplate.RESERVATION_REMINDER,
                    context_data={
                        'reservation_id': str(reservation.id),
                        'table_number': str(reservation.table.number),
                        'party_size': str(reservation.party_size),
                        'start_time': reservation.start_time.strftime('%Y-%m-%d %H:%M'),
                        'restaurant_name': 'Smart Restaurant',  # From settings
                    },
                    related_object=reservation
                )
                
                reminder_count += 1
                logger.info(f"Sent reminder for reservation {reservation.id}")
                
            except Exception as e:
                logger.error(f"Error sending reminder for reservation {reservation.id}: {e}")
                continue
        
        logger.info(f"Sent {reminder_count} reservation reminders")
        return f"Sent {reminder_count} reservation reminders"
        
    except Exception as e:
        logger.error(f"Error sending reservation reminders: {e}")
        raise self.retry(countdown=60 * (2 ** self.retries))


@shared_task(bind=True, max_retries=3)
def auto_confirm_reservations(self):
    """Auto-confirm pending reservations after a certain time"""
    try:
        # Auto-confirm reservations that have been pending for more than 30 minutes
        cutoff_time = timezone.now() - timedelta(minutes=30)
        
        pending_reservations = Reservation.objects.filter(
            status=Reservation.PENDING,
            created_at__lt=cutoff_time
        )
        
        confirmed_count = 0
        
        for reservation in pending_reservations:
            # Check if table is still available
            if ReservationService._is_table_available(
                reservation.table, 
                reservation.start_time, 
                reservation.end_time
            ):
                reservation.status = Reservation.CONFIRMED
                reservation.save()
                confirmed_count += 1
                
                # Send confirmation notification
                try:
                    from notifications.services import NotificationService
                    from notifications.models import NotificationTemplate
                    
                    NotificationService.send_notification(
                        user=reservation.customer,
                        event_type=NotificationTemplate.RESERVATION_CONFIRMED,
                        context_data={
                            'reservation_id': str(reservation.id),
                            'table_number': str(reservation.table.number),
                            'party_size': str(reservation.party_size),
                            'start_time': reservation.start_time.strftime('%Y-%m-%d %H:%M'),
                        },
                        related_object=reservation
                    )
                except Exception as e:
                    logger.error(f"Error sending confirmation for reservation {reservation.id}: {e}")
            else:
                # Table no longer available, cancel reservation
                reservation.status = Reservation.CANCELLED
                reservation.save()
                
                # Send cancellation notification
                try:
                    from notifications.services import NotificationService
                    from notifications.models import NotificationTemplate
                    
                    NotificationService.send_notification(
                        user=reservation.customer,
                        event_type=NotificationTemplate.RESERVATION_CANCELLED,
                        context_data={
                            'reservation_id': str(reservation.id),
                            'table_number': str(reservation.table.number),
                            'start_time': reservation.start_time.strftime('%Y-%m-%d %H:%M'),
                            'reason': 'Table no longer available'
                        },
                        related_object=reservation
                    )
                except Exception as e:
                    logger.error(f"Error sending cancellation for reservation {reservation.id}: {e}")
        
        logger.info(f"Auto-confirmed {confirmed_count} reservations")
        return f"Auto-confirmed {confirmed_count} reservations"
        
    except Exception as e:
        logger.error(f"Error auto-confirming reservations: {e}")
        raise self.retry(countdown=60 * (2 ** self.retries))


@shared_task(bind=True, max_retries=3)
def check_waitlist_availability(self, table_id=None, date_str=None):
    """Check waitlist for newly available slots"""
    try:
        from datetime import date
        
        if date_str:
            check_date = date.fromisoformat(date_str)
        else:
            check_date = date.today()
        
        # Get active waitlist entries for the date
        waitlist_query = ReservationWaitlist.objects.filter(
            preferred_date=check_date,
            is_active=True,
            expires_at__gt=timezone.now()
        ).order_by('created_at')
        
        if table_id:
            # Check specific table
            from .models import Table
            table = Table.objects.get(id=table_id)
            waitlist_query = waitlist_query.filter(
                models.Q(table_preference=table) | models.Q(table_preference__isnull=True)
            )
        
        notified_count = 0
        
        for entry in waitlist_query:
            # Check if there's now availability
            availability = ReservationService.check_availability(
                date=entry.preferred_date,
                start_time=entry.preferred_time,
                duration_minutes=120,  # Assume 2-hour duration
                party_size=entry.party_size,
                table_id=entry.table_preference.id if entry.table_preference else None
            )
            
            if availability['total_available'] > 0:
                # Send notification
                try:
                    from notifications.services import NotificationService
                    
                    # Create a custom notification for waitlist availability
                    NotificationService.send_notification(
                        user=entry.customer,
                        event_type='waitlist_availability',  # Custom event type
                        context_data={
                            'preferred_date': entry.preferred_date.isoformat(),
                            'preferred_time': entry.preferred_time.isoformat(),
                            'party_size': entry.party_size,
                            'available_tables': availability['available_tables'],
                            'waitlist_id': str(entry.id)
                        },
                        related_object=entry
                    )
                    
                    # Mark as notified
                    entry.notified_at = timezone.now()
                    entry.save()
                    
                    notified_count += 1
                    logger.info(f"Notified waitlist customer {entry.customer.username}")
                    
                except Exception as e:
                    logger.error(f"Error notifying waitlist customer {entry.id}: {e}")
                    continue
        
        logger.info(f"Notified {notified_count} waitlist customers")
        return f"Notified {notified_count} waitlist customers"
        
    except Exception as e:
        logger.error(f"Error checking waitlist availability: {e}")
        raise self.retry(countdown=60 * (2 ** self.retries))


@shared_task(bind=True, max_retries=3)
def generate_reservation_analytics(self, date_str=None):
    """Generate reservation analytics for a specific date"""
    try:
        from datetime import date
        from analytics.services import AnalyticsService
        
        if date_str:
            target_date = date.fromisoformat(date_str)
        else:
            target_date = date.today() - timedelta(days=1)
        
        # Get reservation metrics for the date
        reservations = Reservation.objects.filter(
            start_time__date=target_date
        )
        
        total_reservations = reservations.count()
        confirmed_reservations = reservations.filter(status=Reservation.CONFIRMED).count()
        cancelled_reservations = reservations.filter(status=Reservation.CANCELLED).count()
        
        # Calculate table utilization
        from .models import Table
        total_tables = Table.objects.count()
        
        # Track analytics event
        AnalyticsService.track_event(
            event_type='daily_reservation_summary',
            properties={
                'date': target_date.isoformat(),
                'total_reservations': total_reservations,
                'confirmed_reservations': confirmed_reservations,
                'cancelled_reservations': cancelled_reservations,
                'cancellation_rate': (cancelled_reservations / total_reservations * 100) if total_reservations > 0 else 0,
                'table_utilization': (confirmed_reservations / total_tables * 100) if total_tables > 0 else 0
            }
        )
        
        logger.info(f"Generated reservation analytics for {target_date}")
        return f"Generated reservation analytics for {target_date}"
        
    except Exception as e:
        logger.error(f"Error generating reservation analytics: {e}")
        raise self.retry(countdown=60 * (2 ** self.retries))


@shared_task(bind=True, max_retries=3)
def cleanup_old_reservations(self, days_to_keep=365):
    """Clean up old completed reservations"""
    try:
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        
        # Only delete completed/cancelled reservations older than cutoff
        old_reservations = Reservation.objects.filter(
            end_time__lt=cutoff_date,
            status__in=[Reservation.CONFIRMED, Reservation.CANCELLED]
        )
        
        deleted_count = old_reservations.count()
        old_reservations.delete()
        
        logger.info(f"Cleaned up {deleted_count} old reservations")
        return f"Cleaned up {deleted_count} old reservations"
        
    except Exception as e:
        logger.error(f"Error cleaning up old reservations: {e}")
        raise self.retry(countdown=60 * (2 ** self.retries))
