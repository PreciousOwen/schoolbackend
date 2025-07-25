# orders/serializers.py

from django.db import transaction, models
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import serializers

from menu.models import MenuItem
from corporate.models import CorporateStaff
from .models import Order, OrderItem, OrderStatusHistory, OrderNote, KitchenQueue

User = get_user_model()


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_id = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all(),
        source="menu_item",
        write_only=True
    )
    menu_item = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "menu_item",
            "menu_item_id",
            "quantity",
            "unit_price",
            "line_total",
        ]
        read_only_fields = ["id", "unit_price", "line_total"]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be positive")
        if value > 100:
            raise serializers.ValidationError("Quantity too large")
        return value


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    table_number = serializers.CharField(max_length=10, required=False, allow_null=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer', 'items', 'total', 'status',
            'kitchen_notes', 'is_takeout', 'is_delivery', 'table_number',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order_number', 'customer', 'total', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        table_number = validated_data.pop('table_number', None)
        
        order = Order.objects.create(**validated_data)
        
        # Set table number if provided
        if table_number:
            order.table_number = table_number
            order.save()
        
        # Create order items
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        
        return order


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for order status history"""
    changed_by_name = serializers.CharField(source='changed_by.username', read_only=True)

    class Meta:
        model = OrderStatusHistory
        fields = [
            'id', 'previous_status', 'new_status', 'changed_by', 'changed_by_name',
            'notes', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class OrderNoteSerializer(serializers.ModelSerializer):
    """Serializer for order notes"""
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = OrderNote
        fields = ['id', 'note', 'is_internal', 'author', 'author_name', 'created_at']
        read_only_fields = ['id', 'author', 'author_name', 'created_at']


class KitchenQueueSerializer(serializers.ModelSerializer):
    """Serializer for kitchen queue management"""
    order_details = OrderSerializer(source='order', read_only=True)

    class Meta:
        model = KitchenQueue
        fields = [
            'id', 'order', 'order_details', 'queue_position',
            'estimated_start_time', 'notes', 'created_at', 'updated_at'
        ]


class DetailedOrderSerializer(OrderSerializer):
    """Enhanced order serializer with kitchen management fields"""
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    notes = OrderNoteSerializer(many=True, read_only=True)
    kitchen_queue = KitchenQueueSerializer(read_only=True)
    assigned_chef_name = serializers.CharField(source='assigned_chef.username', read_only=True)
    server_name = serializers.CharField(source='server.username', read_only=True)
    estimated_completion_time = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()

    class Meta(OrderSerializer.Meta):
        fields = OrderSerializer.Meta.fields + [
            'kitchen_notes', 'estimated_prep_time', 'actual_prep_time',
            'confirmed_at', 'kitchen_started_at', 'ready_at', 'served_at',
            'assigned_chef', 'assigned_chef_name', 'server', 'server_name',
            'priority', 'is_takeout', 'is_delivery',
            'status_history', 'notes', 'kitchen_queue',
            'estimated_completion_time', 'is_overdue'
        ]
        read_only_fields = OrderSerializer.Meta.read_only_fields + [
            'confirmed_at', 'kitchen_started_at', 'ready_at', 'served_at',
            'estimated_completion_time', 'is_overdue'
        ]

    def get_estimated_completion_time(self, obj):
        completion_time = obj.get_estimated_completion_time()
        return completion_time.isoformat() if completion_time else None

    def get_is_overdue(self, obj):
        return obj.is_overdue()


class UpdateOrderStatusSerializer(serializers.Serializer):
    """Serializer for updating order status"""
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)
    estimated_prep_time = serializers.IntegerField(required=False, min_value=1)
    assigned_chef = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_staff=True),
        required=False,
        allow_null=True
    )
    server = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_staff=True),
        required=False,
        allow_null=True
    )


class KitchenDashboardSerializer(serializers.Serializer):
    """Serializer for kitchen dashboard data"""
    pending_orders = OrderSerializer(many=True, read_only=True)
    preparing_orders = OrderSerializer(many=True, read_only=True)
    ready_orders = OrderSerializer(many=True, read_only=True)
    overdue_orders = OrderSerializer(many=True, read_only=True)
    queue_summary = serializers.SerializerMethodField()

    def get_queue_summary(self, obj):
        return {
            'total_pending': len(obj.get('pending_orders', [])),
            'total_preparing': len(obj.get('preparing_orders', [])),
            'total_ready': len(obj.get('ready_orders', [])),
            'total_overdue': len(obj.get('overdue_orders', [])),
        }
