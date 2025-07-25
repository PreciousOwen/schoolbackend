from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal

class InventoryCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Inventory Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class InventoryItem(models.Model):
    UNIT_CHOICES = [
        ('kg', 'Kilograms'),
        ('g', 'Grams'),
        ('l', 'Liters'),
        ('ml', 'Milliliters'),
        ('pcs', 'Pieces'),
        ('boxes', 'Boxes'),
        ('bags', 'Bags'),
        ('bottles', 'Bottles'),
    ]

    STATUS_CHOICES = [
        ('in-stock', 'In Stock'),
        ('low-stock', 'Low Stock'),
        ('out-of-stock', 'Out of Stock'),
        ('expired', 'Expired'),
    ]

    name = models.CharField(max_length=200)
    category = models.ForeignKey(InventoryCategory, on_delete=models.CASCADE, related_name='items')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')

    # Stock levels
    current_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    min_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    max_stock = models.DecimalField(max_digits=10, decimal_places=2, default=100, validators=[MinValueValidator(0)])

    # Unit and pricing
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='pcs')
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    # Dates and location
    last_restocked = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)

    # Usage tracking
    usage_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text="Average daily usage")

    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in-stock')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ['name', 'category']

    def __str__(self):
        return f"{self.name} ({self.current_stock} {self.unit})"

    @property
    def estimated_days_left(self):
        """Calculate estimated days until stock runs out based on usage rate"""
        if self.usage_rate <= 0 or self.current_stock <= 0:
            return 0
        return int(self.current_stock / self.usage_rate)

    @property
    def total_value(self):
        """Calculate total value of current stock"""
        return self.current_stock * self.cost_per_unit

    def save(self, *args, **kwargs):
        # Auto-update status based on stock levels
        if self.current_stock <= 0:
            self.status = 'out-of-stock'
        elif self.current_stock <= self.min_stock:
            self.status = 'low-stock'
        else:
            self.status = 'in-stock'

        # Check for expiry
        if self.expiry_date:
            from django.utils import timezone
            if self.expiry_date <= timezone.now():
                self.status = 'expired'

        super().save(*args, **kwargs)

class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('adjustment', 'Adjustment'),
        ('expired', 'Expired'),
        ('damaged', 'Damaged'),
    ]

    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    reason = models.CharField(max_length=200)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])

    # Tracking
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.item.name} - {self.movement_type} ({self.quantity} {self.item.unit})"

    def save(self, *args, **kwargs):
        # Update item stock based on movement
        if self.movement_type == 'in':
            self.item.current_stock += self.quantity
        elif self.movement_type in ['out', 'expired', 'damaged']:
            self.item.current_stock = max(0, self.item.current_stock - self.quantity)
        elif self.movement_type == 'adjustment':
            # For adjustments, the quantity represents the new total stock
            self.item.current_stock = self.quantity

        self.item.save()
        super().save(*args, **kwargs)
