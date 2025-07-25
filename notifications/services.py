# notifications/services.py

import logging
from django.conf import settings
from django.core.mail import send_mail
from django.template import Template, Context
from django.utils import timezone
from twilio.rest import Client
from typing import Dict, Any, Optional
from celery import shared_task

from .models import NotificationTemplate, Notification, NotificationPreference

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending notifications"""
    
    @staticmethod
    def send_notification(user, event_type: str, context_data: Dict[str, Any] = None, 
                         related_object=None):
        """Send notification based on event type and user preferences"""
        try:
            # Get user preferences
            prefs, _ = NotificationPreference.objects.get_or_create(user=user)
            
            # Get templates for this event
            templates = NotificationTemplate.objects.filter(
                event_type=event_type, 
                is_active=True
            )
            
            for template in templates:
                should_send = NotificationService._should_send_notification(
                    prefs, template.notification_type, event_type
                )
                
                if should_send:
                    NotificationService._create_and_send_notification(
                        user, template, context_data or {}, related_object
                    )
                    
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
    
    @staticmethod
    def _should_send_notification(prefs: NotificationPreference, 
                                notification_type: str, event_type: str) -> bool:
        """Check if notification should be sent based on user preferences"""
        if notification_type == NotificationTemplate.EMAIL:
            if not prefs.email_enabled:
                return False
            if 'order' in event_type and not prefs.email_order_updates:
                return False
            if 'reservation' in event_type and not prefs.email_reservation_updates:
                return False
            if 'payment' in event_type and not prefs.email_payment_updates:
                return False
                
        elif notification_type == NotificationTemplate.SMS:
            if not prefs.sms_enabled:
                return False
            if 'order' in event_type and not prefs.sms_order_updates:
                return False
            if 'reservation' in event_type and not prefs.sms_reservation_updates:
                return False
            if 'payment' in event_type and not prefs.sms_payment_updates:
                return False
                
        elif notification_type == NotificationTemplate.PUSH:
            if not prefs.push_enabled:
                return False
            if 'order' in event_type and not prefs.push_order_updates:
                return False
            if 'reservation' in event_type and not prefs.push_reservation_updates:
                return False
            if 'payment' in event_type and not prefs.push_payment_updates:
                return False
        
        return True
    
    @staticmethod
    def _create_and_send_notification(user, template: NotificationTemplate, 
                                    context_data: Dict[str, Any], related_object=None):
        """Create notification record and send it"""
        try:
            # Render template content
            context = Context({
                'user': user,
                'restaurant_name': settings.RESTAURANT_NAME,
                'restaurant_email': settings.RESTAURANT_EMAIL,
                'restaurant_phone': settings.RESTAURANT_PHONE,
                **context_data
            })
            
            # Create notification record
            notification = Notification.objects.create(
                recipient=user,
                template=template,
                content_object=related_object,
                recipient_email=user.email,
                recipient_phone=getattr(user.profile, 'phone', '') if hasattr(user, 'profile') else '',
                metadata=context_data
            )
            
            # Send based on type
            if template.notification_type == NotificationTemplate.EMAIL:
                NotificationService._send_email(notification, template, context)
            elif template.notification_type == NotificationTemplate.SMS:
                NotificationService._send_sms(notification, template, context)
            elif template.notification_type == NotificationTemplate.PUSH:
                NotificationService._send_push(notification, template, context)
                
        except Exception as e:
            logger.error(f"Error creating/sending notification: {e}")
    
    @staticmethod
    def _send_email(notification: Notification, template: NotificationTemplate, context: Context):
        """Send email notification"""
        try:
            subject_template = Template(template.subject)
            subject = subject_template.render(context)
            
            if template.html_template:
                html_template = Template(template.html_template)
                html_message = html_template.render(context)
            else:
                html_message = None
            
            text_template = Template(template.text_template or template.html_template)
            text_message = text_template.render(context)
            
            notification.subject = subject
            notification.message = text_message
            notification.save()
            
            # Send email asynchronously
            send_email_task.delay(
                notification.id,
                subject,
                text_message,
                html_message,
                notification.recipient_email
            )
            
        except Exception as e:
            logger.error(f"Error preparing email: {e}")
            notification.status = Notification.FAILED
            notification.error_message = str(e)
            notification.save()
    
    @staticmethod
    def _send_sms(notification: Notification, template: NotificationTemplate, context: Context):
        """Send SMS notification"""
        try:
            sms_template = Template(template.sms_template)
            message = sms_template.render(context)
            
            notification.message = message
            notification.save()
            
            # Send SMS asynchronously
            send_sms_task.delay(notification.id, message, str(notification.recipient_phone))
            
        except Exception as e:
            logger.error(f"Error preparing SMS: {e}")
            notification.status = Notification.FAILED
            notification.error_message = str(e)
            notification.save()
    
    @staticmethod
    def _send_push(notification: Notification, template: NotificationTemplate, context: Context):
        """Send push notification"""
        try:
            title_template = Template(template.push_title)
            body_template = Template(template.push_body)
            
            title = title_template.render(context)
            body = body_template.render(context)
            
            notification.subject = title
            notification.message = body
            notification.save()
            
            # Send push notification asynchronously
            send_push_task.delay(notification.id, title, body, notification.recipient.id)
            
        except Exception as e:
            logger.error(f"Error preparing push notification: {e}")
            notification.status = Notification.FAILED
            notification.error_message = str(e)
            notification.save()


@shared_task(bind=True, max_retries=3)
def send_email_task(self, notification_id: str, subject: str, message: str, 
                   html_message: Optional[str], recipient_email: str):
    """Celery task to send email"""
    try:
        notification = Notification.objects.get(id=notification_id)
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False
        )
        
        notification.status = Notification.SENT
        notification.sent_at = timezone.now()
        notification.save()
        
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        notification = Notification.objects.get(id=notification_id)
        notification.retry_count += 1
        
        if notification.retry_count < notification.max_retries:
            notification.save()
            # Retry with exponential backoff
            raise self.retry(countdown=60 * (2 ** notification.retry_count))
        else:
            notification.status = Notification.FAILED
            notification.error_message = str(e)
            notification.save()


@shared_task(bind=True, max_retries=3)
def send_sms_task(self, notification_id: str, message: str, phone_number: str):
    """Celery task to send SMS"""
    try:
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            raise Exception("Twilio credentials not configured")
        
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        message = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        
        notification = Notification.objects.get(id=notification_id)
        notification.status = Notification.SENT
        notification.sent_at = timezone.now()
        notification.metadata['twilio_sid'] = message.sid
        notification.save()
        
    except Exception as e:
        logger.error(f"Error sending SMS: {e}")
        notification = Notification.objects.get(id=notification_id)
        notification.retry_count += 1
        
        if notification.retry_count < notification.max_retries:
            notification.save()
            raise self.retry(countdown=60 * (2 ** notification.retry_count))
        else:
            notification.status = Notification.FAILED
            notification.error_message = str(e)
            notification.save()


@shared_task(bind=True, max_retries=3)
def send_push_task(self, notification_id: str, title: str, body: str, user_id: int):
    """Celery task to send push notification"""
    try:
        # This would integrate with a push notification service like FCM
        # For now, we'll just mark as sent
        notification = Notification.objects.get(id=notification_id)
        notification.status = Notification.SENT
        notification.sent_at = timezone.now()
        notification.save()
        
        logger.info(f"Push notification sent: {title} - {body}")
        
    except Exception as e:
        logger.error(f"Error sending push notification: {e}")
        notification = Notification.objects.get(id=notification_id)
        notification.retry_count += 1
        
        if notification.retry_count < notification.max_retries:
            notification.save()
            raise self.retry(countdown=60 * (2 ** notification.retry_count))
        else:
            notification.status = Notification.FAILED
            notification.error_message = str(e)
            notification.save()
