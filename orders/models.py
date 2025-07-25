from django.conf import settings
from django.db import models

from menu.models import MenuItem
from corporate.models import CorporateAccount
from reservations.models import Table  # Add this import



class Order(models.Model):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    SERVED = "served"
    PAID = "paid"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (CONFIRMED, "Confirmed"),
        (PREPARING, "Preparing"),
        (READY, "Ready"),
        (SERVED, "Served"),
        (PAID, "Paid"),
        (CANCELLED, "Cancelled"),
        (REFUNDED, "Refunded"),
    ]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Kitchen workflow fields
    kitchen_notes = models.TextField(blank=True, help_text="Special instructions for kitchen")
    estimated_prep_time = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Estimated preparation time in minutes"
    )
    actual_prep_time = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Actual preparation time in minutes"
    )

    # Timestamps for workflow tracking
    confirmed_at = models.DateTimeField(null=True, blank=True)
    kitchen_started_at = models.DateTimeField(null=True, blank=True)
    ready_at = models.DateTimeField(null=True, blank=True)
    served_at = models.DateTimeField(null=True, blank=True)

    # Staff assignments
    assigned_chef = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_orders',
        limit_choices_to={'is_staff': True}
    )
    server = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='served_orders',
        limit_choices_to={'is_staff': True}
    )

    # Priority and special flags
    NORMAL = 'normal'
    HIGH = 'high'
    URGENT = 'urgent'

    PRIORITY_CHOICES = [
        (NORMAL, 'Normal'),
        (HIGH, 'High'),
        (URGENT, 'Urgent'),
    ]

    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=NORMAL)
    is_takeout = models.BooleanField(default=False)
    is_delivery = models.BooleanField(default=False)

    # Corporate account integration
    corporate_account = models.ForeignKey(
        CorporateAccount,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='orders'
    )

    # Add table field if needed for restaurant orders
    table = models.ForeignKey(
        Table,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='orders',
        help_text="Table assignment for dine-in orders"
    )

    # Add table number field
    table_number = models.CharField(
        max_length=10, 
        null=True, 
        blank=True,
        help_text="Table number for dine-in orders"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['customer', 'created_at']),
        ]

    def __str__(self):
        return f"Order #{self.id} by {self.customer.username}"

    def get_estimated_completion_time(self):
        """Calculate estimated completion time based on prep time"""
        if self.estimated_prep_time and self.kitchen_started_at:
            from datetime import timedelta
            return self.kitchen_started_at + timedelta(minutes=self.estimated_prep_time)
        return None

    def is_overdue(self):
        """Check if order is overdue based on estimated completion time"""
        if self.status in [self.PREPARING] and self.get_estimated_completion_time():
            from django.utils import timezone
            return timezone.now() > self.get_estimated_completion_time()
        return False


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    line_total = models.DecimalField(max_digits=8, decimal_places=2)

    def save(self, *args, **kwargs):
        # On create/update, capture menu_item price & compute line_total
        if not self.unit_price:
            self.unit_price = self.menu_item.price
        self.line_total = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}× {self.menu_item.name}"


class OrderStatusHistory(models.Model):
    """Track order status changes for audit and analytics"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    previous_status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES, null=True, blank=True)
    new_status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Order status histories'

    def __str__(self):
        return f"Order #{self.order.id}: {self.previous_status} → {self.new_status}"


class KitchenQueue(models.Model):
    """Manage kitchen queue and order priorities"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='kitchen_queue')
    queue_position = models.PositiveIntegerField(default=0)
    estimated_start_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['queue_position', 'created_at']

    def __str__(self):
        return f"Queue #{self.queue_position}: Order #{self.order.id}"


class OrderNote(models.Model):
    """Staff notes on orders"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    note = models.TextField()
    is_internal = models.BooleanField(default=True, help_text="Internal staff note or customer-visible")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note on Order #{self.order.id} by {self.author.username}"
