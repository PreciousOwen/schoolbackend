from django.conf import settings
from django.db import models


class Table(models.Model):
    number = models.PositiveIntegerField(unique=True)
    seats = models.PositiveIntegerField(default=4)
    description = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["number"]

    def __str__(self):
        return f"Table {self.number} ({self.seats} seats)"


class Reservation(models.Model):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (CONFIRMED, "Confirmed"),
        (CANCELLED, "Cancelled"),
    ]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reservations"
    )
    table = models.ForeignKey(
        Table, on_delete=models.PROTECT, related_name="reservations"
    )
    party_size = models.PositiveIntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_time"]
        unique_together = [["table", "start_time", "end_time"]]

    def __str__(self):
        return f"Resv #{self.id} – {self.customer.username} @ Table {self.table.number}"

    def clean(self):
        """Validate reservation data"""
        from django.core.exceptions import ValidationError
        from django.utils import timezone

        # Check if start time is in the future
        if self.start_time <= timezone.now():
            raise ValidationError("Reservation must be in the future")

        # Check if end time is after start time
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time")

        # Check if party size fits the table
        if self.party_size > self.table.seats:
            raise ValidationError(f"Party size ({self.party_size}) exceeds table capacity ({self.table.seats})")

        # Check for overlapping reservations
        overlapping = Reservation.objects.filter(
            table=self.table,
            status__in=[self.PENDING, self.CONFIRMED],
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError("Table is already reserved for this time period")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def duration_minutes(self):
        """Get reservation duration in minutes"""
        return int((self.end_time - self.start_time).total_seconds() / 60)

    def can_be_cancelled(self):
        """Check if reservation can be cancelled"""
        from django.utils import timezone
        from datetime import timedelta

        # Can cancel up to 2 hours before reservation
        cancellation_deadline = self.start_time - timedelta(hours=2)
        return timezone.now() < cancellation_deadline

    def is_upcoming(self):
        """Check if reservation is upcoming (within next 24 hours)"""
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        return now <= self.start_time <= now + timedelta(hours=24)


class ReservationAvailability(models.Model):
    """Track table availability patterns"""
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='availability_patterns')
    day_of_week = models.PositiveSmallIntegerField(
        choices=[
            (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'),
            (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
        ]
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    max_party_size = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['table', 'day_of_week', 'start_time']
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        day_name = self.get_day_of_week_display()
        return f"Table {self.table.number} - {day_name} {self.start_time}-{self.end_time}"


class ReservationWaitlist(models.Model):
    """Waitlist for fully booked time slots"""
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='waitlist_entries'
    )
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    party_size = models.PositiveIntegerField()
    table_preference = models.ForeignKey(
        Table,
        on_delete=models.CASCADE,
        null=True, blank=True,
        help_text="Preferred table (optional)"
    )

    # Flexibility options
    flexible_date = models.BooleanField(default=False, help_text="Flexible with date")
    flexible_time = models.BooleanField(default=False, help_text="Flexible with time")
    max_wait_days = models.PositiveIntegerField(default=7, help_text="Maximum days to wait")

    # Contact preferences
    notify_by_email = models.BooleanField(default=True)
    notify_by_sms = models.BooleanField(default=False)

    # Status tracking
    is_active = models.BooleanField(default=True)
    notified_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Waitlist: {self.customer.username} for {self.preferred_date} {self.preferred_time}"
