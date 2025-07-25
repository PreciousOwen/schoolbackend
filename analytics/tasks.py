# analytics/tasks.py

from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import date, timedelta
import logging

from .services import AnalyticsService
from .models import AnalyticsEvent

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(bind=True, max_retries=3)
def generate_daily_summaries(self, target_date=None):
    """Generate daily summaries for analytics"""
    try:
        if target_date is None:
            target_date = date.today() - timedelta(days=1)  # Previous day
        elif isinstance(target_date, str):
            target_date = date.fromisoformat(target_date)
        
        summary = AnalyticsService.generate_daily_summary(target_date)
        logger.info(f"Generated daily summary for {target_date}: {summary}")
        
        # Also update menu item analytics
        AnalyticsService.update_menu_item_analytics(target_date)
        
        return f"Daily summary generated for {target_date}"
        
    except Exception as e:
        logger.error(f"Error generating daily summary: {e}")
        raise self.retry(countdown=60 * (2 ** self.retries))


@shared_task(bind=True, max_retries=3)
def update_customer_analytics(self, customer_id):
    """Update analytics for a specific customer"""
    try:
        customer = User.objects.get(id=customer_id)
        analytics = AnalyticsService.update_customer_analytics(customer)
        logger.info(f"Updated analytics for customer {customer.username}")
        return f"Analytics updated for customer {customer_id}"
        
    except User.DoesNotExist:
        logger.error(f"Customer {customer_id} not found")
        return f"Customer {customer_id} not found"
    except Exception as e:
        logger.error(f"Error updating customer analytics: {e}")
        raise self.retry(countdown=60 * (2 ** self.retries))


@shared_task(bind=True, max_retries=3)
def update_all_customer_analytics(self):
    """Update analytics for all customers with recent activity"""
    try:
        # Get customers with activity in the last 30 days
        recent_cutoff = timezone.now() - timedelta(days=30)
        
        # Get customers with recent orders
        from orders.models import Order
        recent_customers = User.objects.filter(
            orders__created_at__gte=recent_cutoff
        ).distinct()
        
        updated_count = 0
        for customer in recent_customers:
            try:
                AnalyticsService.update_customer_analytics(customer)
                updated_count += 1
            except Exception as e:
                logger.error(f"Error updating analytics for customer {customer.id}: {e}")
                continue
        
        logger.info(f"Updated analytics for {updated_count} customers")
        return f"Updated analytics for {updated_count} customers"
        
    except Exception as e:
        logger.error(f"Error in bulk customer analytics update: {e}")
        raise self.retry(countdown=60 * (2 ** self.retries))


@shared_task(bind=True, max_retries=3)
def generate_revenue_report(self, period_type, start_date, end_date):
    """Generate revenue report for a period"""
    try:
        if isinstance(start_date, str):
            start_date = date.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = date.fromisoformat(end_date)
        
        report = AnalyticsService.generate_revenue_report(
            period_type, start_date, end_date
        )
        
        logger.info(f"Generated {period_type} revenue report for {start_date} to {end_date}")
        return f"Revenue report generated: {report.id}"
        
    except Exception as e:
        logger.error(f"Error generating revenue report: {e}")
        raise self.retry(countdown=60 * (2 ** self.retries))


@shared_task(bind=True, max_retries=3)
def cleanup_old_events(self, days_to_keep=90):
    """Clean up old analytics events"""
    try:
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        
        deleted_count, _ = AnalyticsEvent.objects.filter(
            timestamp__lt=cutoff_date
        ).delete()
        
        logger.info(f"Cleaned up {deleted_count} old analytics events")
        return f"Cleaned up {deleted_count} old analytics events"
        
    except Exception as e:
        logger.error(f"Error cleaning up old events: {e}")
        raise self.retry(countdown=60 * (2 ** self.retries))


@shared_task(bind=True, max_retries=3)
def track_event_async(self, event_type, user_id=None, content_type_id=None, 
                     object_id=None, properties=None, session_data=None):
    """Track analytics event asynchronously"""
    try:
        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass
        
        content_object = None
        if content_type_id and object_id:
            from django.contrib.contenttypes.models import ContentType
            try:
                content_type = ContentType.objects.get(id=content_type_id)
                content_object = content_type.get_object_for_this_type(id=object_id)
            except (ContentType.DoesNotExist, Exception):
                pass
        
        event_data = {
            'event_type': event_type,
            'user': user,
            'content_object': content_object,
            'properties': properties or {},
        }
        
        if session_data:
            event_data.update({
                'session_id': session_data.get('session_id'),
                'ip_address': session_data.get('ip_address'),
                'user_agent': session_data.get('user_agent'),
            })
        
        event = AnalyticsEvent.objects.create(**event_data)
        logger.info(f"Tracked event: {event_type}")
        
        return f"Event tracked: {event.id}"
        
    except Exception as e:
        logger.error(f"Error tracking event: {e}")
        raise self.retry(countdown=60 * (2 ** self.retries))


@shared_task(bind=True, max_retries=3)
def calculate_customer_ltv(self, customer_id):
    """Calculate customer lifetime value"""
    try:
        customer = User.objects.get(id=customer_id)
        
        # Get customer analytics
        from .models import CustomerAnalytics
        analytics, created = CustomerAnalytics.objects.get_or_create(
            customer=customer
        )
        
        # Simple LTV calculation: avg_order_value * order_frequency * customer_lifespan
        # This is a simplified model - in practice you'd use more sophisticated algorithms
        
        if analytics.total_orders > 0:
            # Estimate order frequency (orders per month)
            if analytics.days_since_last_visit:
                days_active = max(analytics.days_since_last_visit, 30)
            else:
                days_active = 30
            
            order_frequency = analytics.total_orders / (days_active / 30.0)
            
            # Estimate customer lifespan based on visit frequency
            lifespan_months = {
                'daily': 24,
                'weekly': 18,
                'monthly': 12,
                'occasional': 6,
                'new': 3
            }.get(analytics.visit_frequency, 6)
            
            # Calculate LTV
            ltv = float(analytics.avg_order_value) * order_frequency * lifespan_months
            
            # Calculate churn risk (simplified)
            if analytics.days_since_last_visit:
                if analytics.days_since_last_visit > 90:
                    churn_risk = 0.8
                elif analytics.days_since_last_visit > 60:
                    churn_risk = 0.6
                elif analytics.days_since_last_visit > 30:
                    churn_risk = 0.3
                else:
                    churn_risk = 0.1
            else:
                churn_risk = 0.1
            
            analytics.ltv_score = ltv
            analytics.churn_risk_score = churn_risk
            analytics.save()
            
            logger.info(f"Calculated LTV for customer {customer.username}: ${ltv:.2f}")
            return f"LTV calculated: ${ltv:.2f}, Churn risk: {churn_risk:.2f}"
        
        return "Insufficient data for LTV calculation"
        
    except User.DoesNotExist:
        logger.error(f"Customer {customer_id} not found")
        return f"Customer {customer_id} not found"
    except Exception as e:
        logger.error(f"Error calculating LTV: {e}")
        raise self.retry(countdown=60 * (2 ** self.retries))


@shared_task(bind=True, max_retries=3)
def generate_weekly_reports(self):
    """Generate weekly reports for management"""
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        # Generate revenue report
        revenue_report = AnalyticsService.generate_revenue_report(
            'weekly', start_date, end_date
        )
        
        # Update customer analytics for active customers
        update_all_customer_analytics.delay()
        
        # Generate daily summaries for any missing days
        for i in range(7):
            check_date = start_date + timedelta(days=i)
            generate_daily_summaries.delay(check_date.isoformat())
        
        logger.info(f"Generated weekly reports for {start_date} to {end_date}")
        return f"Weekly reports generated for {start_date} to {end_date}"
        
    except Exception as e:
        logger.error(f"Error generating weekly reports: {e}")
        raise self.retry(countdown=60 * (2 ** self.retries))
