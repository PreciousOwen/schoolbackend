# notifications/models.py

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from phonenumber_field.modelfields import PhoneNumberField
import uuid


class NotificationTemplate(models.Model):
    """Templates for different types of notifications"""
    EMAIL = 'email'
    SMS = 'sms'
    PUSH = 'push'

    TYPE_CHOICES = [
        (EMAIL, 'Email'),
        (SMS, 'SMS'),
        (PUSH, 'Push Notification'),
    ]

    # Event types
    ORDER_CONFIRMED = 'order_confirmed'
    ORDER_READY = 'order_ready'
    ORDER_CANCELLED = 'order_cancelled'
    PAYMENT_SUCCESS = 'payment_success'
    PAYMENT_FAILED = 'payment_failed'
    RESERVATION_CONFIRMED = 'reservation_confirmed'
    RESERVATION_REMINDER = 'reservation_reminder'
    RESERVATION_CANCELLED = 'reservation_cancelled'
    WELCOME = 'welcome'
    PASSWORD_RESET = 'password_reset'

    EVENT_CHOICES = [
        (ORDER_CONFIRMED, 'Order Confirmed'),
        (ORDER_READY, 'Order Ready'),
        (ORDER_CANCELLED, 'Order Cancelled'),
        (PAYMENT_SUCCESS, 'Payment Success'),
        (PAYMENT_FAILED, 'Payment Failed'),
        (RESERVATION_CONFIRMED, 'Reservation Confirmed'),
        (RESERVATION_REMINDER, 'Reservation Reminder'),
        (RESERVATION_CANCELLED, 'Reservation Cancelled'),
        (WELCOME, 'Welcome'),
        (PASSWORD_RESET, 'Password Reset'),
    ]

    name = models.CharField(max_length=100)
    event_type = models.CharField(max_length=50, choices=EVENT_CHOICES)
    notification_type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    # Email specific fields
    subject = models.CharField(max_length=200, blank=True)
    html_template = models.TextField(blank=True)
    text_template = models.TextField(blank=True)

    # SMS specific fields
    sms_template = models.TextField(blank=True)

    # Push notification fields
    push_title = models.CharField(max_length=100, blank=True)
    push_body = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['event_type', 'notification_type']

    def __str__(self):
        return f"{self.name} ({self.get_notification_type_display()})"


class Notification(models.Model):
    """Individual notification records"""
    PENDING = 'pending'
    SENT = 'sent'
    FAILED = 'failed'
    DELIVERED = 'delivered'
    READ = 'read'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (SENT, 'Sent'),
        (FAILED, 'Failed'),
        (DELIVERED, 'Delivered'),
        (READ, 'Read'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.PROTECT,
        related_name='notifications'
    )

    # Generic foreign key to link to any model (Order, Reservation, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Notification content
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()

    # Delivery details
    recipient_email = models.EmailField(blank=True)
    recipient_phone = PhoneNumberField(blank=True)

    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    # Error tracking
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['template', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.template.name} to {self.recipient.username}"


class NotificationPreference(models.Model):
    """User preferences for notifications"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )

    # Email preferences
    email_enabled = models.BooleanField(default=True)
    email_order_updates = models.BooleanField(default=True)
    email_reservation_updates = models.BooleanField(default=True)
    email_payment_updates = models.BooleanField(default=True)
    email_marketing = models.BooleanField(default=False)

    # SMS preferences
    sms_enabled = models.BooleanField(default=False)
    sms_order_updates = models.BooleanField(default=False)
    sms_reservation_updates = models.BooleanField(default=False)
    sms_payment_updates = models.BooleanField(default=False)

    # Push notification preferences
    push_enabled = models.BooleanField(default=True)
    push_order_updates = models.BooleanField(default=True)
    push_reservation_updates = models.BooleanField(default=True)
    push_payment_updates = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user.username}"
