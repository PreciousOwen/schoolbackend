from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import InventoryItem, InventoryCategory, Supplier, StockMovement
from .serializers import (
    InventoryItemSerializer, InventoryCategorySerializer,
    SupplierSerializer, StockMovementSerializer, InventoryStatsSerializer
)

class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.filter(is_active=True)
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__name__icontains=category)

        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by supplier
        supplier = self.request.query_params.get('supplier')
        if supplier:
            queryset = queryset.filter(supplier__name__icontains=supplier)

        # Search by name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(category__name__icontains=search) |
                Q(supplier__name__icontains=search)
            )

        return queryset.select_related('category', 'supplier')

    @action(detail=True, methods=['post'])
    def movement(self, request, pk=None):
        """Add stock movement for an item"""
        item = self.get_object()

        movement_type = request.data.get('type')
        quantity = request.data.get('quantity')
        reason = request.data.get('reason', '')
        cost = request.data.get('cost')

        if not movement_type or not quantity:
            return Response(
                {'error': 'Movement type and quantity are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity = Decimal(str(quantity))
            if quantity <= 0:
                return Response(
                    {'error': 'Quantity must be positive'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid quantity'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create stock movement
        movement = StockMovement.objects.create(
            item=item,
            movement_type=movement_type,
            quantity=quantity,
            reason=reason,
            cost=cost,
            user=request.user
        )

        serializer = StockMovementSerializer(movement)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get inventory statistics"""
        items = InventoryItem.objects.filter(is_active=True)

        # Calculate stats
        total_items = items.count()
        low_stock_items = items.filter(status='low-stock').count()
        out_of_stock_items = items.filter(status='out-of-stock').count()

        # Items expiring in next 7 days
        next_week = timezone.now() + timedelta(days=7)
        expiring_soon = items.filter(
            expiry_date__lte=next_week,
            expiry_date__gt=timezone.now()
        ).count()

        # Total inventory value
        total_value = sum(item.total_value for item in items)

        # Monthly usage (mock calculation)
        monthly_usage = sum(item.usage_rate * 30 * item.cost_per_unit for item in items)

        stats_data = {
            'total_items': total_items,
            'low_stock_items': low_stock_items,
            'out_of_stock_items': out_of_stock_items,
            'expiring_soon': expiring_soon,
            'total_value': total_value,
            'monthly_usage': monthly_usage
        }

        serializer = InventoryStatsSerializer(stats_data)
        return Response(serializer.data)

class InventoryCategoryViewSet(viewsets.ModelViewSet):
    queryset = InventoryCategory.objects.all()
    serializer_class = InventoryCategorySerializer
    permission_classes = [IsAuthenticated]

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.filter(is_active=True)
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]

class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by item
        item_id = self.request.query_params.get('item')
        if item_id:
            queryset = queryset.filter(item_id=item_id)

        # Filter by movement type
        movement_type = self.request.query_params.get('type')
        if movement_type:
            queryset = queryset.filter(movement_type=movement_type)

        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)

        return queryset.select_related('item', 'user')
