# notifications/views.py

from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from .models import Notification, NotificationTemplate, NotificationPreference
from .serializers import (
    NotificationSerializer, NotificationTemplateSerializer,
    NotificationPreferenceSerializer, MarkNotificationReadSerializer,
    SendTestNotificationSerializer
)
from .services import NotificationService


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """View user notifications"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'template__event_type', 'template__notification_type']
    ordering_fields = ['created_at', 'sent_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=False, methods=['post'])
    def mark_read(self, request):
        """Mark notifications as read"""
        serializer = MarkNotificationReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        notification_ids = serializer.validated_data['notification_ids']

        updated_count = Notification.objects.filter(
            id__in=notification_ids,
            recipient=request.user,
            status__in=[Notification.SENT, Notification.DELIVERED]
        ).update(
            status=Notification.READ,
            read_at=timezone.now()
        )

        return Response({
            'message': f'{updated_count} notifications marked as read'
        })

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = Notification.objects.filter(
            recipient=request.user,
            status__in=[Notification.SENT, Notification.DELIVERED]
        ).count()

        return Response({'unread_count': count})


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    """Manage notification templates (staff only)"""
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['event_type', 'notification_type', 'is_active']

    @action(detail=True, methods=['post'])
    def send_test(self, request, pk=None):
        """Send test notification"""
        template = self.get_object()
        serializer = SendTestNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        test_data = serializer.validated_data.get('test_data', {})
        test_data.update({
            'order_id': '12345',
            'order_total': '25.99',
            'reservation_time': '2024-01-15 19:00',
            'table_number': '5'
        })

        NotificationService.send_notification(
            user=request.user,
            event_type=template.event_type,
            context_data=test_data
        )

        return Response({'message': 'Test notification sent'})


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """Manage user notification preferences"""
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)

    def get_object(self):
        """Get or create preferences for the current user"""
        prefs, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return prefs

    def list(self, request, *args, **kwargs):
        """Return user's preferences"""
        prefs = self.get_object()
        serializer = self.get_serializer(prefs)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """Update user's preferences"""
        prefs = self.get_object()
        serializer = self.get_serializer(prefs, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Create/update preferences (same as update)"""
        return self.update(request, *args, **kwargs)
