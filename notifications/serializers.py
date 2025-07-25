# notifications/serializers.py

from rest_framework import serializers
from .models import Notification, NotificationTemplate, NotificationPreference


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for notification templates"""
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'event_type', 'notification_type',
            'subject', 'html_template', 'text_template', 'sms_template',
            'push_title', 'push_body', 'is_active', 'created_at', 'updated_at'
        ]


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications"""
    template_name = serializers.CharField(source='template.name', read_only=True)
    event_type = serializers.CharField(source='template.event_type', read_only=True)
    notification_type = serializers.CharField(source='template.notification_type', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'template_name', 'event_type', 'notification_type',
            'subject', 'message', 'status', 'sent_at', 'delivered_at',
            'read_at', 'error_message', 'created_at'
        ]
        read_only_fields = [
            'id', 'template_name', 'event_type', 'notification_type',
            'subject', 'message', 'status', 'sent_at', 'delivered_at',
            'error_message', 'created_at'
        ]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for notification preferences"""
    
    class Meta:
        model = NotificationPreference
        fields = [
            'email_enabled', 'email_order_updates', 'email_reservation_updates',
            'email_payment_updates', 'email_marketing',
            'sms_enabled', 'sms_order_updates', 'sms_reservation_updates',
            'sms_payment_updates',
            'push_enabled', 'push_order_updates', 'push_reservation_updates',
            'push_payment_updates'
        ]


class MarkNotificationReadSerializer(serializers.Serializer):
    """Serializer for marking notifications as read"""
    notification_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False
    )


class SendTestNotificationSerializer(serializers.Serializer):
    """Serializer for sending test notifications"""
    event_type = serializers.ChoiceField(choices=NotificationTemplate.EVENT_CHOICES)
    notification_type = serializers.ChoiceField(choices=NotificationTemplate.TYPE_CHOICES)
    test_data = serializers.JSONField(required=False, default=dict)
