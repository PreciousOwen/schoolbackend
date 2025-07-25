# analytics/services.py

from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from orders.models import Order, OrderItem
from reservations.models import Reservation
from payments.models import Payment
from menu.models import MenuItem
from .models import (
    AnalyticsEvent, DailySummary, MenuItemAnalytics, 
    CustomerAnalytics, RevenueReport
)


class AnalyticsService:
    """Service for analytics data processing and reporting"""
    
    @staticmethod
    def track_event(event_type: str, user=None, content_object=None, 
                   properties: Dict = None, request=None):
        """Track an analytics event"""
        
        event_data = {
            'event_type': event_type,
            'user': user,
            'content_object': content_object,
            'properties': properties or {},
        }
        
        if request:
            event_data.update({
                'session_id': request.session.session_key,
                'ip_address': AnalyticsService._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            })
        
        return AnalyticsEvent.objects.create(**event_data)
    
    @staticmethod
    def _get_client_ip(request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def generate_daily_summary(target_date: date = None) -> DailySummary:
        """Generate daily summary for a specific date"""
        
        if target_date is None:
            target_date = date.today()
        
        # Get or create daily summary
        summary, created = DailySummary.objects.get_or_create(
            date=target_date,
            defaults={}
        )
        
        # Calculate order metrics
        orders = Order.objects.filter(created_at__date=target_date)
        completed_orders = orders.filter(status=Order.SERVED)
        cancelled_orders = orders.filter(status=Order.CANCELLED)
        
        # Calculate revenue from completed orders
        total_revenue = completed_orders.aggregate(
            total=Sum('total')
        )['total'] or Decimal('0.00')
        
        avg_order_value = completed_orders.aggregate(
            avg=Avg('total')
        )['avg'] or Decimal('0.00')
        
        # Calculate reservation metrics
        reservations = Reservation.objects.filter(start_time__date=target_date)
        completed_reservations = reservations.filter(status=Reservation.CONFIRMED)
        cancelled_reservations = reservations.filter(status=Reservation.CANCELLED)
        
        total_covers = completed_reservations.aggregate(
            total=Sum('party_size')
        )['total'] or 0
        
        # Calculate customer metrics
        new_customers = AnalyticsEvent.objects.filter(
            event_type=AnalyticsEvent.USER_REGISTERED,
            timestamp__date=target_date
        ).count()
        
        # Calculate operational metrics
        avg_prep_time = completed_orders.aggregate(
            avg=Avg('actual_prep_time')
        )['avg']
        
        # Update summary
        summary.total_orders = orders.count()
        summary.completed_orders = completed_orders.count()
        summary.cancelled_orders = cancelled_orders.count()
        summary.total_revenue = total_revenue
        summary.avg_order_value = avg_order_value
        summary.total_reservations = reservations.count()
        summary.completed_reservations = completed_reservations.count()
        summary.cancelled_reservations = cancelled_reservations.count()
        summary.total_covers = total_covers
        summary.new_customers = new_customers
        summary.avg_prep_time = avg_prep_time
        summary.save()
        
        return summary
    
    @staticmethod
    def update_menu_item_analytics(target_date: date = None):
        """Update menu item analytics for a specific date"""
        
        if target_date is None:
            target_date = date.today()
        
        # Get all menu items that were ordered on this date
        order_items = OrderItem.objects.filter(
            order__created_at__date=target_date,
            order__status__in=[Order.SERVED, Order.PAID]
        ).select_related('menu_item')
        
        # Group by menu item
        menu_item_data = {}
        for item in order_items:
            menu_item_id = item.menu_item.id
            if menu_item_id not in menu_item_data:
                menu_item_data[menu_item_id] = {
                    'menu_item': item.menu_item,
                    'times_ordered': 0,
                    'total_quantity': 0,
                    'total_revenue': Decimal('0.00'),
                }
            
            menu_item_data[menu_item_id]['times_ordered'] += 1
            menu_item_data[menu_item_id]['total_quantity'] += item.quantity
            menu_item_data[menu_item_id]['total_revenue'] += item.line_total
        
        # Update or create analytics records
        for data in menu_item_data.values():
            analytics, created = MenuItemAnalytics.objects.get_or_create(
                menu_item=data['menu_item'],
                date=target_date,
                defaults=data
            )
            
            if not created:
                analytics.times_ordered = data['times_ordered']
                analytics.total_quantity = data['total_quantity']
                analytics.total_revenue = data['total_revenue']
                analytics.save()
    
    @staticmethod
    def update_customer_analytics(customer):
        """Update analytics for a specific customer"""
        
        analytics, created = CustomerAnalytics.objects.get_or_create(
            customer=customer,
            defaults={}
        )
        
        # Calculate order metrics
        orders = Order.objects.filter(customer=customer)
        completed_orders = orders.filter(status__in=[Order.SERVED, Order.PAID])
        
        total_spent = completed_orders.aggregate(
            total=Sum('total')
        )['total'] or Decimal('0.00')
        
        avg_order_value = completed_orders.aggregate(
            avg=Avg('total')
        )['avg'] or Decimal('0.00')
        
        last_order = completed_orders.order_by('-created_at').first()
        
        # Calculate reservation metrics
        reservations = Reservation.objects.filter(customer=customer)
        last_reservation = reservations.order_by('-start_time').first()
        
        # Calculate visit frequency
        if last_order:
            days_since_last = (timezone.now().date() - last_order.created_at.date()).days
            
            if completed_orders.count() >= 10:
                if days_since_last <= 7:
                    frequency = 'weekly'
                elif days_since_last <= 30:
                    frequency = 'monthly'
                else:
                    frequency = 'occasional'
            elif completed_orders.count() >= 3:
                frequency = 'monthly'
            else:
                frequency = 'new'
        else:
            days_since_last = None
            frequency = 'new'
        
        # Get favorite menu items
        favorite_items = OrderItem.objects.filter(
            order__customer=customer,
            order__status__in=[Order.SERVED, Order.PAID]
        ).values('menu_item__name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        favorite_menu_items = [item['menu_item__name'] for item in favorite_items]
        
        # Update analytics
        analytics.total_orders = completed_orders.count()
        analytics.total_spent = total_spent
        analytics.avg_order_value = avg_order_value
        analytics.last_order_date = last_order.created_at if last_order else None
        analytics.total_reservations = reservations.count()
        analytics.last_reservation_date = last_reservation.start_time if last_reservation else None
        analytics.days_since_last_visit = days_since_last
        analytics.visit_frequency = frequency
        analytics.favorite_menu_items = favorite_menu_items
        analytics.save()
        
        return analytics
    
    @staticmethod
    def generate_revenue_report(period_type: str, start_date: date, end_date: date) -> RevenueReport:
        """Generate revenue report for a period"""
        
        # Get or create report
        report, created = RevenueReport.objects.get_or_create(
            period_type=period_type,
            start_date=start_date,
            end_date=end_date,
            defaults={}
        )
        
        # Get completed orders in the period
        orders = Order.objects.filter(
            created_at__date__range=[start_date, end_date],
            status__in=[Order.SERVED, Order.PAID]
        )
        
        # Calculate revenue by category
        food_items = OrderItem.objects.filter(
            order__in=orders,
            menu_item__category__name__icontains='food'
        ).aggregate(total=Sum('line_total'))['total'] or Decimal('0.00')
        
        beverage_items = OrderItem.objects.filter(
            order__in=orders,
            menu_item__category__name__icontains='beverage'
        ).aggregate(total=Sum('line_total'))['total'] or Decimal('0.00')
        
        total_revenue = orders.aggregate(
            total=Sum('total')
        )['total'] or Decimal('0.00')
        
        # Calculate covers (people served)
        reservations = Reservation.objects.filter(
            start_time__date__range=[start_date, end_date],
            status=Reservation.CONFIRMED
        )
        total_covers = reservations.aggregate(
            total=Sum('party_size')
        )['total'] or 0
        
        # Calculate average check size
        avg_check_size = orders.aggregate(
            avg=Avg('total')
        )['avg'] or Decimal('0.00')
        
        # Update report
        report.food_revenue = food_items
        report.beverage_revenue = beverage_items
        report.total_revenue = total_revenue
        report.total_orders = orders.count()
        report.total_covers = total_covers
        report.avg_check_size = avg_check_size
        
        # Calculate gross profit (simplified - would need cost data)
        # For now, assume 30% cost of goods
        report.cost_of_goods = total_revenue * Decimal('0.30')
        report.gross_profit = total_revenue - report.cost_of_goods
        if total_revenue > 0:
            report.gross_margin = (report.gross_profit / total_revenue) * 100
        
        report.save()
        return report
    
    @staticmethod
    def get_dashboard_metrics(days: int = 30) -> Dict:
        """Get key metrics for dashboard"""
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get recent summaries
        summaries = DailySummary.objects.filter(
            date__range=[start_date, end_date]
        )
        
        # Calculate totals
        total_revenue = summaries.aggregate(
            total=Sum('total_revenue')
        )['total'] or Decimal('0.00')
        
        total_orders = summaries.aggregate(
            total=Sum('total_orders')
        )['total'] or 0
        
        total_customers = summaries.aggregate(
            total=Sum('new_customers')
        )['total'] or 0
        
        avg_order_value = summaries.aggregate(
            avg=Avg('avg_order_value')
        )['avg'] or Decimal('0.00')
        
        # Get top menu items
        top_items = MenuItemAnalytics.objects.filter(
            date__range=[start_date, end_date]
        ).values('menu_item__name').annotate(
            total_quantity=Sum('total_quantity'),
            total_revenue=Sum('total_revenue')
        ).order_by('-total_quantity')[:10]
        
        # Get recent trends
        daily_revenue = list(summaries.values('date', 'total_revenue').order_by('date'))
        
        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'totals': {
                'revenue': float(total_revenue),
                'orders': total_orders,
                'customers': total_customers,
                'avg_order_value': float(avg_order_value)
            },
            'top_menu_items': list(top_items),
            'daily_revenue': daily_revenue,
            'growth_rates': AnalyticsService._calculate_growth_rates(summaries)
        }
    
    @staticmethod
    def _calculate_growth_rates(summaries):
        """Calculate growth rates from summaries"""
        if summaries.count() < 2:
            return {}
        
        # Split into two halves for comparison
        mid_point = summaries.count() // 2
        recent_summaries = summaries[:mid_point]
        older_summaries = summaries[mid_point:]
        
        recent_revenue = recent_summaries.aggregate(
            total=Sum('total_revenue')
        )['total'] or Decimal('0.00')
        
        older_revenue = older_summaries.aggregate(
            total=Sum('total_revenue')
        )['total'] or Decimal('0.00')
        
        if older_revenue > 0:
            revenue_growth = ((recent_revenue - older_revenue) / older_revenue) * 100
        else:
            revenue_growth = 0
        
        return {
            'revenue_growth': float(revenue_growth)
        }
