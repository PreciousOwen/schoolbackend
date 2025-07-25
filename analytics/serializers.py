# analytics/serializers.py

from rest_framework import serializers
from datetime import date, timedelta

from .models import (
    AnalyticsEvent, DailySummary, MenuItemAnalytics, 
    CustomerAnalytics, RevenueReport
)


class AnalyticsEventSerializer(serializers.ModelSerializer):
    """Serializer for analytics events"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AnalyticsEvent
        fields = [
            'id', 'event_type', 'user', 'user_name', 'properties',
            'session_id', 'ip_address', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class DailySummarySerializer(serializers.ModelSerializer):
    """Serializer for daily summaries"""
    
    class Meta:
        model = DailySummary
        fields = [
            'date', 'total_orders', 'completed_orders', 'cancelled_orders',
            'total_revenue', 'avg_order_value', 'total_reservations',
            'completed_reservations', 'cancelled_reservations', 'total_covers',
            'new_customers', 'returning_customers', 'avg_prep_time',
            'table_turnover_rate', 'created_at', 'updated_at'
        ]


class MenuItemAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for menu item analytics"""
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    menu_item_category = serializers.CharField(source='menu_item.category.name', read_only=True)
    
    class Meta:
        model = MenuItemAnalytics
        fields = [
            'id', 'menu_item', 'menu_item_name', 'menu_item_category',
            'date', 'times_ordered', 'total_quantity', 'total_revenue',
            'avg_rating', 'times_viewed', 'conversion_rate'
        ]


class CustomerAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for customer analytics"""
    customer_name = serializers.CharField(source='customer.username', read_only=True)
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    
    class Meta:
        model = CustomerAnalytics
        fields = [
            'customer', 'customer_name', 'customer_email', 'total_orders',
            'total_spent', 'avg_order_value', 'last_order_date',
            'total_reservations', 'last_reservation_date', 'preferred_table_size',
            'days_since_last_visit', 'visit_frequency', 'favorite_menu_items',
            'preferred_order_times', 'ltv_score', 'churn_risk_score'
        ]


class RevenueReportSerializer(serializers.ModelSerializer):
    """Serializer for revenue reports"""
    
    class Meta:
        model = RevenueReport
        fields = [
            'id', 'period_type', 'start_date', 'end_date', 'food_revenue',
            'beverage_revenue', 'total_revenue', 'cost_of_goods',
            'gross_profit', 'gross_margin', 'total_orders', 'total_covers',
            'avg_check_size', 'created_at'
        ]


class DashboardMetricsSerializer(serializers.Serializer):
    """Serializer for dashboard metrics"""
    period = serializers.DictField()
    totals = serializers.DictField()
    top_menu_items = serializers.ListField()
    daily_revenue = serializers.ListField()
    growth_rates = serializers.DictField()


class DateRangeSerializer(serializers.Serializer):
    """Serializer for date range queries"""
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    
    def validate(self, data):
        start_date = data['start_date']
        end_date = data['end_date']
        
        if start_date > end_date:
            raise serializers.ValidationError("Start date must be before end date")
        
        if end_date > date.today():
            raise serializers.ValidationError("End date cannot be in the future")
        
        # Limit to 1 year range
        if (end_date - start_date).days > 365:
            raise serializers.ValidationError("Date range cannot exceed 1 year")
        
        return data


class ReportParametersSerializer(serializers.Serializer):
    """Serializer for report parameters"""
    period_type = serializers.ChoiceField(choices=RevenueReport.PERIOD_CHOICES)
    start_date = serializers.DateField()
    end_date = serializers.DateField(required=False)
    
    def validate(self, data):
        start_date = data['start_date']
        period_type = data['period_type']
        
        # Auto-calculate end_date based on period_type if not provided
        if 'end_date' not in data or not data['end_date']:
            if period_type == RevenueReport.DAILY:
                data['end_date'] = start_date
            elif period_type == RevenueReport.WEEKLY:
                data['end_date'] = start_date + timedelta(days=6)
            elif period_type == RevenueReport.MONTHLY:
                # Get last day of month
                if start_date.month == 12:
                    next_month = start_date.replace(year=start_date.year + 1, month=1)
                else:
                    next_month = start_date.replace(month=start_date.month + 1)
                data['end_date'] = next_month - timedelta(days=1)
            elif period_type == RevenueReport.QUARTERLY:
                # Get last day of quarter
                quarter_end_month = ((start_date.month - 1) // 3 + 1) * 3
                if quarter_end_month == 12:
                    quarter_end = start_date.replace(year=start_date.year + 1, month=1) - timedelta(days=1)
                else:
                    quarter_end = start_date.replace(month=quarter_end_month + 1) - timedelta(days=1)
                data['end_date'] = quarter_end
            elif period_type == RevenueReport.YEARLY:
                data['end_date'] = start_date.replace(year=start_date.year + 1) - timedelta(days=1)
        
        # Validate the calculated/provided end_date
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Start date must be before end date")
        
        return data


class MenuPerformanceSerializer(serializers.Serializer):
    """Serializer for menu performance analysis"""
    menu_item_id = serializers.IntegerField()
    menu_item_name = serializers.CharField()
    category = serializers.CharField()
    total_orders = serializers.IntegerField()
    total_quantity = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    avg_rating = serializers.DecimalField(max_digits=3, decimal_places=2, allow_null=True)
    profit_margin = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    popularity_rank = serializers.IntegerField()


class CustomerSegmentSerializer(serializers.Serializer):
    """Serializer for customer segmentation"""
    segment_name = serializers.CharField()
    customer_count = serializers.IntegerField()
    avg_order_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    avg_visit_frequency = serializers.CharField()
    characteristics = serializers.ListField()


class SalesAnalyticsSerializer(serializers.Serializer):
    """Serializer for sales analytics"""
    date_range = serializers.DictField()
    revenue_trend = serializers.ListField()
    order_trend = serializers.ListField()
    peak_hours = serializers.ListField()
    top_performing_days = serializers.ListField()
    seasonal_patterns = serializers.DictField()


class OperationalMetricsSerializer(serializers.Serializer):
    """Serializer for operational metrics"""
    avg_prep_time = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True)
    order_accuracy = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    table_turnover_rate = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    staff_efficiency = serializers.DictField()
    kitchen_performance = serializers.DictField()
    customer_satisfaction = serializers.DecimalField(max_digits=3, decimal_places=2, allow_null=True)
