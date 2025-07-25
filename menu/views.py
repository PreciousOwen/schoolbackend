# menu/views.py

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Max
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from accounts.authentication import CSRFExemptSessionAuthentication
from smartrestaurant.cache import CacheService, cache_menu_items

from .models import Category, MenuItem
from .permissions import IsStaffOrReadOnly
from .serializers import CategorySerializer, MenuItemSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD for Categories. Readable by anyone, writable by staff only.
    """

    authentication_classes = (CSRFExemptSessionAuthentication,)
    permission_classes = (IsStaffOrReadOnly,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def list(self, request, *args, **kwargs):
        """List of categories"""
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def menu_items(self, request, pk=None):
        """Get menu items for this category"""
        category = self.get_object()

        # Use cached query
        cache_key = CacheService.make_key(
            "category_items", category.id,
            prefix=CacheService.MENU_PREFIX
        )

        items = CacheService.get(cache_key)
        if items is None:
            items = MenuItem.objects.filter(
                category=category, available=True
            ).select_related('category')
            CacheService.set(cache_key, list(items), CacheService.MENU_TIMEOUT)

        serializer = MenuItemSerializer(items, many=True, context={'request': request})
        return Response(serializer.data)

@method_decorator(cache_page(60 * 15), name='list')  # Cache for 15 minutes
class MenuItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    CRUD for MenuItems. Readable by anyone, writable by staff only.
    Supports stock updates, search, ordering & filtering.
    """

    authentication_classes = (CSRFExemptSessionAuthentication,)
    permission_classes = (IsStaffOrReadOnly,)

    queryset = MenuItem.objects.select_related("category").all()
    serializer_class = MenuItemSerializer

    # Enable filtering by category and availability
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ("category", "available")
    search_fields = ("name", "description")
    ordering_fields = ("price", "stock", "name", "updated_at")

    def get_queryset(self):
        """Optimize queryset with caching for read operations"""
        queryset = super().get_queryset()

        # For list view, use cached available items if no filters
        if (self.action == 'list' and
            not self.request.query_params and
            not getattr(self.request.user, 'is_staff', False)):

            cache_key = CacheService.make_key(
                "available_items",
                prefix=CacheService.MENU_PREFIX
            )

            cached_items = CacheService.get(cache_key)
            if cached_items is not None:
                # Return cached queryset
                return MenuItem.objects.filter(
                    id__in=[item.id for item in cached_items]
                ).select_related('category')

        return queryset

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured menu items"""
        cache_key = CacheService.make_key(
            "featured_items",
            prefix=CacheService.MENU_PREFIX
        )

        featured_items = CacheService.get(cache_key)
        if featured_items is None:
            featured_items = MenuItem.objects.filter(
                available=True
            ).select_related('category')[:6]
            CacheService.set(cache_key, list(featured_items), CacheService.MENU_TIMEOUT)

        serializer = self.get_serializer(featured_items, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def track_view(self, request, pk=None):
        """Track menu item views for analytics"""
        menu_item = self.get_object()

        # Track view asynchronously
        from analytics.tasks import track_event_async
        track_event_async.delay(
            event_type='menu_item_viewed',
            user_id=request.user.id if request.user.is_authenticated else None,
            content_type_id=menu_item._meta.model._meta.pk.related_model._meta.pk if hasattr(menu_item._meta.model._meta.pk, 'related_model') else None,
            object_id=menu_item.id,
            session_data={
                'session_id': request.session.session_key,
                'ip_address': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            }
        )

        return Response({'status': 'view tracked'})

    @action(detail=False, methods=['get'])
    def check_updates(self, request):
        """
        Lightweight endpoint to check for menu updates
        Returns last update timestamp and item count for change detection
        """
        available_items = self.get_queryset().filter(available=True)

        # Get the most recent update timestamp
        last_updated = available_items.aggregate(
            last_update=Max('updated_at')
        )['last_update']

        # Get current item count
        item_count = available_items.count()

        # Get available category count
        category_count = available_items.values('category').distinct().count()

        return Response({
            'last_updated': last_updated,
            'item_count': item_count,
            'category_count': category_count,
            'timestamp': timezone.now(),
            'status': 'success'
        })

    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
