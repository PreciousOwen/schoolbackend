from rest_framework import serializers
from .models import InventoryItem, InventoryCategory, Supplier, StockMovement

class InventoryCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryCategory
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'contact_person', 'email', 'phone', 'address', 'is_active', 'created_at', 'updated_at']

class InventoryItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    estimated_days_left = serializers.ReadOnlyField()
    total_value = serializers.ReadOnlyField()

    class Meta:
        model = InventoryItem
        fields = [
            'id', 'name', 'category', 'category_name', 'supplier', 'supplier_name',
            'current_stock', 'min_stock', 'max_stock', 'unit', 'cost_per_unit',
            'last_restocked', 'expiry_date', 'location', 'usage_rate', 'status',
            'is_active', 'estimated_days_left', 'total_value', 'created_at', 'updated_at'
        ]

class StockMovementSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = StockMovement
        fields = [
            'id', 'item', 'item_name', 'movement_type', 'quantity', 'reason',
            'cost', 'user', 'user_name', 'timestamp', 'notes'
        ]

class InventoryStatsSerializer(serializers.Serializer):
    total_items = serializers.IntegerField()
    low_stock_items = serializers.IntegerField()
    out_of_stock_items = serializers.IntegerField()
    expiring_soon = serializers.IntegerField()
    total_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    monthly_usage = serializers.DecimalField(max_digits=12, decimal_places=2)
