# analytics/models.py

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal
import uuid
from orders.models import Order
from django.utils import timezone


class AnalyticsEvent(models.Model):
    """Track business events for analytics"""

    # Event types
    ORDER_CREATED = 'order_created'
    ORDER_COMPLETED = 'order_completed'
    ORDER_CANCELLED = 'order_cancelled'
    PAYMENT_COMPLETED = 'payment_completed'
    PAYMENT_FAILED = 'payment_failed'
    RESERVATION_CREATED = 'reservation_created'
    RESERVATION_COMPLETED = 'reservation_completed'
    RESERVATION_CANCELLED = 'reservation_cancelled'
    USER_REGISTERED = 'user_registered'
    USER_LOGIN = 'user_login'
    MENU_ITEM_VIEWED = 'menu_item_viewed'

    EVENT_CHOICES = [
        (ORDER_CREATED, 'Order Created'),
        (ORDER_COMPLETED, 'Order Completed'),
        (ORDER_CANCELLED, 'Order Cancelled'),
        (PAYMENT_COMPLETED, 'Payment Completed'),
        (PAYMENT_FAILED, 'Payment Failed'),
        (RESERVATION_CREATED, 'Reservation Created'),
        (RESERVATION_COMPLETED, 'Reservation Completed'),
        (RESERVATION_CANCELLED, 'Reservation Cancelled'),
        (USER_REGISTERED, 'User Registered'),
        (USER_LOGIN, 'User Login'),
        (MENU_ITEM_VIEWED, 'Menu Item Viewed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=50, choices=EVENT_CHOICES)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='analytics_events'
    )

    # Generic foreign key to link to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Event data
    properties = models.JSONField(default=dict, blank=True)
    session_id = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.timestamp}"


class DailySummary(models.Model):
    """Daily business summary for quick reporting"""
    date = models.DateField(unique=True)

    # Order metrics
    total_orders = models.PositiveIntegerField(default=0)
    completed_orders = models.PositiveIntegerField(default=0)
    cancelled_orders = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    avg_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    # Reservation metrics
    total_reservations = models.PositiveIntegerField(default=0)
    completed_reservations = models.PositiveIntegerField(default=0)
    cancelled_reservations = models.PositiveIntegerField(default=0)
    total_covers = models.PositiveIntegerField(default=0)  # Total people served

    # Customer metrics
    new_customers = models.PositiveIntegerField(default=0)
    returning_customers = models.PositiveIntegerField(default=0)

    # Operational metrics
    avg_prep_time = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    table_turnover_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Summary for {self.date}"


class MenuItemAnalytics(models.Model):
    """Analytics for menu items"""
    menu_item = models.ForeignKey(
        'menu.MenuItem',
        on_delete=models.CASCADE,
        related_name='analytics'
    )
    date = models.DateField()

    # Sales metrics
    times_ordered = models.PositiveIntegerField(default=0)
    total_quantity = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    # Performance metrics
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    times_viewed = models.PositiveIntegerField(default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['menu_item', 'date']
        ordering = ['-date', '-times_ordered']

    def __str__(self):
        return f"{self.menu_item.name} - {self.date}"


class CustomerAnalytics(models.Model):
    """Customer behavior analytics"""
    customer = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='analytics'
    )

    # Order behavior
    total_orders = models.PositiveIntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    avg_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    last_order_date = models.DateTimeField(null=True, blank=True)

    # Reservation behavior
    total_reservations = models.PositiveIntegerField(default=0)
    last_reservation_date = models.DateTimeField(null=True, blank=True)
    preferred_table_size = models.PositiveIntegerField(null=True, blank=True)

    # Engagement metrics
    days_since_last_visit = models.PositiveIntegerField(null=True, blank=True)
    visit_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('occasional', 'Occasional'),
            ('new', 'New Customer'),
        ],
        default='new'
    )

    # Preferences
    favorite_menu_items = models.JSONField(default=list, blank=True)
    preferred_order_times = models.JSONField(default=list, blank=True)

    # Lifetime value
    ltv_score = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    churn_risk_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-total_spent']

    def __str__(self):
        return f"Analytics for {self.customer.username}"


class RevenueReport(models.Model):
    """Periodic revenue reports"""
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    QUARTERLY = 'quarterly'
    YEARLY = 'yearly'

    PERIOD_CHOICES = [
        (DAILY, 'Daily'),
        (WEEKLY, 'Weekly'),
        (MONTHLY, 'Monthly'),
        (QUARTERLY, 'Quarterly'),
        (YEARLY, 'Yearly'),
    ]

    period_type = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()

    # Revenue breakdown
    food_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    beverage_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    # Costs and margins
    cost_of_goods = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    gross_profit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    gross_margin = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))

    # Volume metrics
    total_orders = models.PositiveIntegerField(default=0)
    total_covers = models.PositiveIntegerField(default=0)
    avg_check_size = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['period_type', 'start_date', 'end_date']
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.get_period_type_display()} Report: {self.start_date} to {self.end_date}"


class CompletedOrderAnalytics(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    completion_time = models.DateTimeField(default=timezone.now)
    preparation_duration = models.DurationField(null=True, blank=True)
    total_items = models.IntegerField()
    revenue = models.DecimalField(max_digits=10, decimal_places=2)
    customer_satisfaction = models.IntegerField(null=True, blank=True)  # 1-5 rating
    
    class Meta:
        db_table = 'completed_order_analytics'
        ordering = ['-completion_time']


class PopularDishAnalytics(models.Model):
    dish_name = models.CharField(max_length=200)
    order_count = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'popular_dish_analytics'
        ordering = ['-order_count']
