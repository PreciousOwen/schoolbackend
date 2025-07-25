from rest_framework import serializers
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Reservation, Table, ReservationAvailability, ReservationWaitlist
from .services import ReservationService


class TableSerializer(serializers.ModelSerializer):
    current_availability = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = ["id", "number", "seats", "description", "current_availability"]

    def get_current_availability(self, obj):
        """Get current availability status for the table"""
        now = timezone.now()
        current_reservations = Reservation.objects.filter(
            table=obj,
            start_time__lte=now,
            end_time__gte=now,
            status__in=[Reservation.CONFIRMED, Reservation.PENDING]
        )
        return not current_reservations.exists()


class ReservationAvailabilitySerializer(serializers.ModelSerializer):
    """Serializer for table availability patterns"""

    class Meta:
        model = ReservationAvailability
        fields = [
            'id', 'table', 'day_of_week', 'start_time', 'end_time',
            'is_available', 'max_party_size', 'notes'
        ]


class ReservationSerializer(serializers.ModelSerializer):
    table_details = TableSerializer(source='table', read_only=True)
    customer_name = serializers.CharField(source='customer.username', read_only=True)
    duration_minutes = serializers.ReadOnlyField()
    can_be_cancelled = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()

    class Meta:
        model = Reservation
        fields = [
            "id", "customer", "customer_name", "table", "table_details",
            "party_size", "start_time", "end_time", "status",
            "duration_minutes", "can_be_cancelled", "is_upcoming",
            "created_at", "updated_at"
        ]
        read_only_fields = ["status", "created_at", "updated_at"]

    def validate(self, data):
        """Validate reservation data"""
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        party_size = data.get('party_size')
        table = data.get('table')

        # Basic validations
        if start_time <= timezone.now():
            raise serializers.ValidationError("Reservation must be in the future")

        if end_time <= start_time:
            raise serializers.ValidationError("End time must be after start time")

        if party_size > table.seats:
            raise serializers.ValidationError(
                f"Party size ({party_size}) exceeds table capacity ({table.seats})"
            )

        # Check availability
        if not ReservationService._is_table_available(table, start_time, end_time):
            raise serializers.ValidationError("Table is not available for the requested time")

        return data


class CheckAvailabilitySerializer(serializers.Serializer):
    """Serializer for checking table availability"""
    date = serializers.DateField()
    time = serializers.TimeField()
    duration_minutes = serializers.IntegerField(min_value=30, max_value=480, default=120)
    party_size = serializers.IntegerField(min_value=1, max_value=20)
    table_id = serializers.IntegerField(required=False)


class CreateReservationSerializer(serializers.Serializer):
    """Serializer for creating reservations"""
    table_id = serializers.IntegerField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    party_size = serializers.IntegerField(min_value=1, max_value=20)
    special_requests = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        start_time = data['start_time']
        end_time = data['end_time']

        if start_time <= timezone.now():
            raise serializers.ValidationError("Reservation must be in the future")

        if end_time <= start_time:
            raise serializers.ValidationError("End time must be after start time")

        # Check if duration is reasonable (30 minutes to 8 hours)
        duration = (end_time - start_time).total_seconds() / 60
        if not 30 <= duration <= 480:
            raise serializers.ValidationError("Reservation duration must be between 30 minutes and 8 hours")

        return data


class ReservationWaitlistSerializer(serializers.ModelSerializer):
    """Serializer for waitlist entries"""
    customer_name = serializers.CharField(source='customer.username', read_only=True)
    table_number = serializers.IntegerField(source='table_preference.number', read_only=True)

    class Meta:
        model = ReservationWaitlist
        fields = [
            'id', 'customer', 'customer_name', 'preferred_date', 'preferred_time',
            'party_size', 'table_preference', 'table_number', 'flexible_date',
            'flexible_time', 'max_wait_days', 'notify_by_email', 'notify_by_sms',
            'is_active', 'created_at', 'expires_at'
        ]
        read_only_fields = ['customer', 'created_at', 'expires_at']


class AddToWaitlistSerializer(serializers.Serializer):
    """Serializer for adding to waitlist"""
    preferred_date = serializers.DateField()
    preferred_time = serializers.TimeField()
    party_size = serializers.IntegerField(min_value=1, max_value=20)
    table_preference = serializers.IntegerField(required=False)
    flexible_date = serializers.BooleanField(default=False)
    flexible_time = serializers.BooleanField(default=False)
    max_wait_days = serializers.IntegerField(min_value=1, max_value=30, default=7)
    notify_by_email = serializers.BooleanField(default=True)
    notify_by_sms = serializers.BooleanField(default=False)


class DailyScheduleSerializer(serializers.Serializer):
    """Serializer for daily reservation schedule"""
    date = serializers.DateField()


class UpdateReservationStatusSerializer(serializers.Serializer):
    """Serializer for updating reservation status"""
    status = serializers.ChoiceField(choices=Reservation.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)
