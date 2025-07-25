from django.utils import timezone
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.authentication import CSRFExemptSessionAuthentication

from .models import Order, OrderStatusHistory, OrderNote, KitchenQueue
from .permissions import IsOwnerOrStaff
from .serializers import (
    OrderSerializer, DetailedOrderSerializer, UpdateOrderStatusSerializer,
    OrderNoteSerializer, KitchenDashboardSerializer, KitchenQueueSerializer
)


class OrderViewSet(viewsets.ModelViewSet):
    authentication_classes = (CSRFExemptSessionAuthentication,)
    permission_classes = (IsOwnerOrStaff,)
    serializer_class = OrderSerializer
    queryset = Order.objects.prefetch_related("items__menu_item").select_related(
        "customer", "assigned_chef", "server", "corporate_account"
    ).all()

    # Filters for dashboards
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    filterset_fields = ["status", "customer", "priority", "assigned_chef", "is_takeout", "is_delivery"]
    search_fields = ["customer__username", "items__menu_item__name", "kitchen_notes"]
    ordering_fields = ["created_at", "total", "priority", "estimated_prep_time"]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            return DetailedOrderSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        # Ensure the 'customer' is always the logged-in user
        order = serializer.save(customer=self.request.user)

        # Create status history entry
        OrderStatusHistory.objects.create(
            order=order,
            new_status=order.status,
            changed_by=self.request.user,
            notes="Order created"
        )

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update order status with workflow tracking"""
        order = self.get_object()
        serializer = UpdateOrderStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_status = order.status
        new_status = serializer.validated_data['status']
        notes = serializer.validated_data.get('notes', '')

        # Update order fields based on status
        if new_status == Order.CONFIRMED and old_status == Order.PENDING:
            order.confirmed_at = timezone.now()
        elif new_status == Order.PREPARING and old_status in [Order.CONFIRMED, Order.PENDING]:
            order.kitchen_started_at = timezone.now()
            if 'assigned_chef' in serializer.validated_data:
                order.assigned_chef = serializer.validated_data['assigned_chef']
            if 'estimated_prep_time' in serializer.validated_data:
                order.estimated_prep_time = serializer.validated_data['estimated_prep_time']
        elif new_status == Order.READY and old_status == Order.PREPARING:
            order.ready_at = timezone.now()
            if order.kitchen_started_at:
                # Calculate actual prep time
                prep_time = (timezone.now() - order.kitchen_started_at).total_seconds() / 60
                order.actual_prep_time = int(prep_time)
        elif new_status == Order.SERVED and old_status == Order.READY:
            order.served_at = timezone.now()
            if 'server' in serializer.validated_data:
                order.server = serializer.validated_data['server']

        order.status = new_status
        order.save()

        # Create status history entry
        OrderStatusHistory.objects.create(
            order=order,
            previous_status=old_status,
            new_status=new_status,
            changed_by=request.user,
            notes=notes
        )

        response_serializer = DetailedOrderSerializer(order, context={'request': request})
        return Response(response_serializer.data)

    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        """Add a note to an order"""
        order = self.get_object()
        serializer = OrderNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        note = serializer.save(order=order, author=request.user)
        response_serializer = OrderNoteSerializer(note)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def kitchen_dashboard(self, request):
        """Get kitchen dashboard data"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Staff access required'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get orders by status
        pending_orders = Order.objects.filter(
            status__in=[Order.PENDING, Order.CONFIRMED]
        ).prefetch_related('items__menu_item')

        preparing_orders = Order.objects.filter(
            status=Order.PREPARING
        ).prefetch_related('items__menu_item')

        ready_orders = Order.objects.filter(
            status=Order.READY
        ).prefetch_related('items__menu_item')

        # Get overdue orders
        overdue_orders = [order for order in preparing_orders if order.is_overdue()]

        dashboard_data = {
            'pending_orders': pending_orders,
            'preparing_orders': preparing_orders,
            'ready_orders': ready_orders,
            'overdue_orders': overdue_orders,
        }

        serializer = KitchenDashboardSerializer(dashboard_data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        """Get orders assigned to the current staff member"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Staff access required'},
                status=status.HTTP_403_FORBIDDEN
            )

        orders = Order.objects.filter(
            Q(assigned_chef=request.user) | Q(server=request.user)
        ).prefetch_related('items__menu_item')

        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def kitchen_queue(self, request):
        """Get orders for kitchen display - excludes completed/cancelled orders"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Staff access required'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get only active orders (not completed, cancelled, or served)
        active_orders = Order.objects.filter(
            status__in=[Order.PENDING, Order.CONFIRMED, Order.PREPARING, Order.READY]
        ).select_related('customer').prefetch_related('items__menu_item').order_by('created_at')

        serializer = self.get_serializer(active_orders, many=True)
        return Response(serializer.data)


class KitchenQueueViewSet(viewsets.ModelViewSet):
    """Manage kitchen queue"""
    serializer_class = KitchenQueueSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_staff:
            return KitchenQueue.objects.none()
        return KitchenQueue.objects.select_related('order__customer').all()

    @action(detail=False, methods=['post'])
    def reorder_queue(self, request):
        """Reorder the kitchen queue"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Staff access required'},
                status=status.HTTP_403_FORBIDDEN
            )

        queue_items = request.data.get('queue_items', [])

        for item in queue_items:
            try:
                queue_obj = KitchenQueue.objects.get(id=item['id'])
                queue_obj.queue_position = item['position']
                queue_obj.save()
            except KitchenQueue.DoesNotExist:
                continue

        return Response({'message': 'Queue reordered successfully'})


class OrderAnalyticsViewSet(viewsets.ViewSet):
    """Order analytics and reporting"""
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['get'])
    def daily_summary(self, request):
        """Get daily order summary"""
        from django.db.models import Count, Sum, Avg
        from datetime import date, timedelta

        today = date.today()
        yesterday = today - timedelta(days=1)

        # Today's stats
        today_orders = Order.objects.filter(created_at__date=today)
        today_stats = today_orders.aggregate(
            total_orders=Count('id'),
            total_revenue=Sum('total'),
            avg_order_value=Avg('total'),
            avg_prep_time=Avg('actual_prep_time')
        )

        # Yesterday's stats for comparison
        yesterday_orders = Order.objects.filter(created_at__date=yesterday)
        yesterday_stats = yesterday_orders.aggregate(
            total_orders=Count('id'),
            total_revenue=Sum('total'),
            avg_order_value=Avg('total'),
            avg_prep_time=Avg('actual_prep_time')
        )

        # Status breakdown
        status_breakdown = today_orders.values('status').annotate(
            count=Count('id')
        ).order_by('status')

        return Response({
            'date': today,
            'today': today_stats,
            'yesterday': yesterday_stats,
            'status_breakdown': list(status_breakdown),
            'peak_hours': self._get_peak_hours(today_orders)
        })

    def _get_peak_hours(self, orders):
        """Calculate peak hours from orders"""
        from django.db.models import Count

        hourly_orders = orders.extra(
            select={'hour': 'EXTRACT(hour FROM created_at)'}
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('-count')[:3]

        return list(hourly_orders)
