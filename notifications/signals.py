# notifications/signals.py

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from orders.models import Order
from payments.models import Payment
from reservations.models import Reservation
from .services import NotificationService
from .models import NotificationTemplate

User = get_user_model()


@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):
    """Send notifications when order status changes"""
    if created:
        # New order created
        NotificationService.send_notification(
            user=instance.customer,
            event_type=NotificationTemplate.ORDER_CONFIRMED,
            context_data={
                'order_id': str(instance.id),
                'order_total': str(instance.total),
                'order_items': [
                    {
                        'name': item.menu_item.name,
                        'quantity': item.quantity,
                        'price': str(item.unit_price)
                    }
                    for item in instance.items.all()
                ]
            },
            related_object=instance
        )
    else:
        # Order status updated
        if hasattr(instance, '_previous_status'):
            if (instance._previous_status != instance.status and 
                instance.status == Order.READY):
                NotificationService.send_notification(
                    user=instance.customer,
                    event_type=NotificationTemplate.ORDER_READY,
                    context_data={
                        'order_id': str(instance.id),
                        'order_total': str(instance.total),
                    },
                    related_object=instance
                )
            elif (instance._previous_status != instance.status and 
                  instance.status == Order.CANCELLED):
                NotificationService.send_notification(
                    user=instance.customer,
                    event_type=NotificationTemplate.ORDER_CANCELLED,
                    context_data={
                        'order_id': str(instance.id),
                        'order_total': str(instance.total),
                    },
                    related_object=instance
                )


@receiver(pre_save, sender=Order)
def store_previous_order_status(sender, instance, **kwargs):
    """Store previous status to detect changes"""
    if instance.pk:
        try:
            previous = Order.objects.get(pk=instance.pk)
            instance._previous_status = previous.status
        except Order.DoesNotExist:
            instance._previous_status = None


@receiver(post_save, sender=Payment)
def payment_status_changed(sender, instance, created, **kwargs):
    """Send notifications when payment status changes"""
    if not created and hasattr(instance, '_previous_status'):
        if (instance._previous_status != instance.status and 
            instance.status == Payment.SUCCEEDED):
            NotificationService.send_notification(
                user=instance.order.customer,
                event_type=NotificationTemplate.PAYMENT_SUCCESS,
                context_data={
                    'payment_id': str(instance.id),
                    'order_id': str(instance.order.id),
                    'amount': str(instance.amount),
                    'currency': instance.currency,
                    'receipt_url': instance.receipt_url,
                },
                related_object=instance
            )
        elif (instance._previous_status != instance.status and 
              instance.status == Payment.FAILED):
            NotificationService.send_notification(
                user=instance.order.customer,
                event_type=NotificationTemplate.PAYMENT_FAILED,
                context_data={
                    'payment_id': str(instance.id),
                    'order_id': str(instance.order.id),
                    'amount': str(instance.amount),
                    'currency': instance.currency,
                    'failure_reason': instance.failure_reason,
                },
                related_object=instance
            )


@receiver(pre_save, sender=Payment)
def store_previous_payment_status(sender, instance, **kwargs):
    """Store previous status to detect changes"""
    if instance.pk:
        try:
            previous = Payment.objects.get(pk=instance.pk)
            instance._previous_status = previous.status
        except Payment.DoesNotExist:
            instance._previous_status = None


@receiver(post_save, sender=Reservation)
def reservation_status_changed(sender, instance, created, **kwargs):
    """Send notifications when reservation status changes"""
    if created:
        # New reservation created
        NotificationService.send_notification(
            user=instance.customer,
            event_type=NotificationTemplate.RESERVATION_CONFIRMED,
            context_data={
                'reservation_id': str(instance.id),
                'table_number': str(instance.table.number),
                'party_size': str(instance.party_size),
                'start_time': instance.start_time.strftime('%Y-%m-%d %H:%M'),
                'end_time': instance.end_time.strftime('%Y-%m-%d %H:%M'),
            },
            related_object=instance
        )
    else:
        # Reservation status updated
        if hasattr(instance, '_previous_status'):
            if (instance._previous_status != instance.status and 
                instance.status == Reservation.CANCELLED):
                NotificationService.send_notification(
                    user=instance.customer,
                    event_type=NotificationTemplate.RESERVATION_CANCELLED,
                    context_data={
                        'reservation_id': str(instance.id),
                        'table_number': str(instance.table.number),
                        'start_time': instance.start_time.strftime('%Y-%m-%d %H:%M'),
                    },
                    related_object=instance
                )


@receiver(pre_save, sender=Reservation)
def store_previous_reservation_status(sender, instance, **kwargs):
    """Store previous status to detect changes"""
    if instance.pk:
        try:
            previous = Reservation.objects.get(pk=instance.pk)
            instance._previous_status = previous.status
        except Reservation.DoesNotExist:
            instance._previous_status = None


@receiver(post_save, sender=User)
def send_welcome_notification(sender, instance, created, **kwargs):
    """Send welcome notification to new users"""
    if created:
        NotificationService.send_notification(
            user=instance,
            event_type=NotificationTemplate.WELCOME,
            context_data={
                'username': instance.username,
                'first_name': instance.first_name or instance.username,
            },
            related_object=instance
        )
