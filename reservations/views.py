from django.utils import timezone
from django.db.models import Q
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime, date, time

from accounts.authentication import CSRFExemptSessionAuthentication

from .models import Reservation, Table, ReservationWaitlist
from .serializers import (
    ReservationSerializer, TableSerializer, CheckAvailabilitySerializer,
    CreateReservationSerializer, ReservationWaitlistSerializer,
    AddToWaitlistSerializer, DailyScheduleSerializer,
    UpdateReservationStatusSerializer
)
from .services import ReservationService


class TableViewSet(viewsets.ModelViewSet):
    authentication_classes = (CSRFExemptSessionAuthentication,)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Table.objects.all()
    serializer_class = TableSerializer

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """Get availability for a specific table"""
        table = self.get_object()

        # Get date from query params (default to today)
        date_str = request.query_params.get('date', date.today().isoformat())
        try:
            check_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get reservations for this table on this date
        reservations = Reservation.objects.filter(
            table=table,
            start_time__date=check_date,
            status__in=[Reservation.PENDING, Reservation.CONFIRMED]
        ).order_by('start_time')

        reservation_data = []
        for reservation in reservations:
            reservation_data.append({
                'id': reservation.id,
                'start_time': reservation.start_time.isoformat(),
                'end_time': reservation.end_time.isoformat(),
                'party_size': reservation.party_size,
                'status': reservation.status
            })

        return Response({
            'table_id': table.id,
            'table_number': table.number,
            'date': check_date.isoformat(),
            'reservations': reservation_data
        })


class ReservationViewSet(viewsets.ModelViewSet):
    authentication_classes = (CSRFExemptSessionAuthentication,)
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReservationSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Reservation.objects.select_related("table", "customer").all()
        return Reservation.objects.filter(customer=self.request.user).select_related("table")

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateReservationSerializer
        return ReservationSerializer

    def create(self, request, *args, **kwargs):
        """Create a new reservation"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Use the reservation service to create the reservation
        success, message, reservation = ReservationService.create_reservation(
            customer=request.user,
            table_id=serializer.validated_data['table_id'],
            start_datetime=serializer.validated_data['start_time'],
            end_datetime=serializer.validated_data['end_time'],
            party_size=serializer.validated_data['party_size'],
            special_requests=serializer.validated_data.get('special_requests', '')
        )

        if success:
            response_serializer = ReservationSerializer(reservation, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def check_availability(self, request):
        """Check table availability"""
        serializer = CheckAvailabilitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        availability = ReservationService.check_availability(
            date=serializer.validated_data['date'],
            start_time=serializer.validated_data['time'],
            duration_minutes=serializer.validated_data['duration_minutes'],
            party_size=serializer.validated_data['party_size'],
            table_id=serializer.validated_data.get('table_id')
        )

        return Response(availability)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update reservation status (staff only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Staff access required'},
                status=status.HTTP_403_FORBIDDEN
            )

        reservation = self.get_object()
        serializer = UpdateReservationStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_status = reservation.status
        new_status = serializer.validated_data['status']

        reservation.status = new_status
        reservation.save()

        # You could add status history tracking here similar to orders

        response_serializer = ReservationSerializer(reservation, context={'request': request})
        return Response(response_serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a reservation"""
        reservation = self.get_object()

        # Check if user can cancel this reservation
        if reservation.customer != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only cancel your own reservations'},
                status=status.HTTP_403_FORBIDDEN
            )

        if not reservation.can_be_cancelled():
            return Response(
                {'error': 'Reservation cannot be cancelled (less than 2 hours before start time)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        reservation.status = Reservation.CANCELLED
        reservation.save()

        response_serializer = ReservationSerializer(reservation, context={'request': request})
        return Response(response_serializer.data)

    @action(detail=False, methods=['post'])
    def add_to_waitlist(self, request):
        """Add customer to waitlist when no tables available"""
        serializer = AddToWaitlistSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check if there's actually no availability
        availability = ReservationService.check_availability(
            date=serializer.validated_data['preferred_date'],
            start_time=serializer.validated_data['preferred_time'],
            duration_minutes=120,  # Default 2 hours
            party_size=serializer.validated_data['party_size'],
            table_id=serializer.validated_data.get('table_preference')
        )

        if availability['total_available'] > 0:
            return Response(
                {'error': 'Tables are available for this time. Please make a direct reservation.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get table preference if specified
        table_preference = None
        if 'table_preference' in serializer.validated_data:
            try:
                table_preference = Table.objects.get(id=serializer.validated_data['table_preference'])
            except Table.DoesNotExist:
                return Response(
                    {'error': 'Invalid table preference'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Add to waitlist
        waitlist_entry = ReservationService.add_to_waitlist(
            customer=request.user,
            preferred_date=serializer.validated_data['preferred_date'],
            preferred_time=serializer.validated_data['preferred_time'],
            party_size=serializer.validated_data['party_size'],
            table_preference=table_preference,
            flexible_options={
                'flexible_date': serializer.validated_data['flexible_date'],
                'flexible_time': serializer.validated_data['flexible_time'],
                'max_wait_days': serializer.validated_data['max_wait_days'],
                'notify_by_email': serializer.validated_data['notify_by_email'],
                'notify_by_sms': serializer.validated_data['notify_by_sms'],
            }
        )

        response_serializer = ReservationWaitlistSerializer(waitlist_entry)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def daily_schedule(self, request):
        """Get daily reservation schedule (staff only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Staff access required'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = DailyScheduleSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        schedule_date = serializer.validated_data['date']
        schedule = ReservationService.get_daily_schedule(schedule_date)

        return Response({
            'date': schedule_date.isoformat(),
            'schedule': schedule
        })

    @action(detail=False, methods=['get'])
    def my_waitlist(self, request):
        """Get user's waitlist entries"""
        waitlist_entries = ReservationWaitlist.objects.filter(
            customer=request.user,
            is_active=True,
            expires_at__gt=timezone.now()
        ).order_by('created_at')

        serializer = ReservationWaitlistSerializer(waitlist_entries, many=True)
        return Response(serializer.data)


class WaitlistViewSet(viewsets.ReadOnlyModelViewSet):
    """Manage reservation waitlist (staff only)"""
    serializer_class = ReservationWaitlistSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return ReservationWaitlist.objects.select_related('customer', 'table_preference').all()

    @action(detail=True, methods=['post'])
    def notify_customer(self, request, pk=None):
        """Manually notify a waitlist customer"""
        waitlist_entry = self.get_object()

        # Check current availability
        availability = ReservationService.check_availability(
            date=waitlist_entry.preferred_date,
            start_time=waitlist_entry.preferred_time,
            duration_minutes=120,
            party_size=waitlist_entry.party_size,
            table_id=waitlist_entry.table_preference.id if waitlist_entry.table_preference else None
        )

        if availability['total_available'] == 0:
            return Response(
                {'error': 'No tables available for this customer yet'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mark as notified
        waitlist_entry.notified_at = timezone.now()
        waitlist_entry.save()

        # Here you would send the actual notification
        # NotificationService.send_notification(...)

        return Response({'message': 'Customer notified successfully'})


class ReservationAnalyticsViewSet(viewsets.ViewSet):
    """Reservation analytics and reporting"""
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['get'])
    def occupancy_report(self, request):
        """Get table occupancy report"""
        from django.db.models import Count, Avg
        from datetime import date, timedelta

        # Get date range from query params
        start_date = request.query_params.get('start_date', (date.today() - timedelta(days=7)).isoformat())
        end_date = request.query_params.get('end_date', date.today().isoformat())

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get reservations in date range
        reservations = Reservation.objects.filter(
            start_time__date__range=[start_date, end_date],
            status__in=[Reservation.CONFIRMED, Reservation.SERVED]
        )

        # Calculate occupancy by table
        table_stats = reservations.values('table__number').annotate(
            total_reservations=Count('id'),
            avg_party_size=Avg('party_size'),
            total_covers=Count('party_size')
        ).order_by('table__number')

        # Calculate daily occupancy
        daily_stats = reservations.extra(
            select={'date': 'DATE(start_time)'}
        ).values('date').annotate(
            total_reservations=Count('id'),
            total_covers=Count('party_size')
        ).order_by('date')

        # Peak hours analysis
        hourly_stats = reservations.extra(
            select={'hour': 'EXTRACT(hour FROM start_time)'}
        ).values('hour').annotate(
            reservation_count=Count('id')
        ).order_by('hour')

        return Response({
            'date_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'table_occupancy': list(table_stats),
            'daily_occupancy': list(daily_stats),
            'peak_hours': list(hourly_stats),
            'summary': {
                'total_reservations': reservations.count(),
                'total_covers': sum(r.party_size for r in reservations),
                'avg_party_size': reservations.aggregate(Avg('party_size'))['party_size__avg'],
                'cancellation_rate': self._calculate_cancellation_rate(start_date, end_date)
            }
        })

    def _calculate_cancellation_rate(self, start_date, end_date):
        """Calculate cancellation rate for the period"""
        total_reservations = Reservation.objects.filter(
            created_at__date__range=[start_date, end_date]
        ).count()

        cancelled_reservations = Reservation.objects.filter(
            created_at__date__range=[start_date, end_date],
            status=Reservation.CANCELLED
        ).count()

        if total_reservations == 0:
            return 0

        return round((cancelled_reservations / total_reservations) * 100, 2)
