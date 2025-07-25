# smartrestaurant/cache.py

from django.core.cache import cache
from django.conf import settings
from functools import wraps
import hashlib
import json
from typing import Any, Optional, Callable


class CacheService:
    """Service for managing application caching"""
    
    # Cache key prefixes
    MENU_PREFIX = "menu"
    ANALYTICS_PREFIX = "analytics"
    RESERVATION_PREFIX = "reservation"
    USER_PREFIX = "user"
    
    # Cache timeouts (in seconds)
    MENU_TIMEOUT = 60 * 15  # 15 minutes
    ANALYTICS_TIMEOUT = 60 * 60  # 1 hour
    RESERVATION_TIMEOUT = 60 * 5  # 5 minutes
    USER_TIMEOUT = 60 * 30  # 30 minutes
    
    @staticmethod
    def make_key(*args, prefix: str = "") -> str:
        """Generate a cache key from arguments"""
        key_parts = [str(arg) for arg in args if arg is not None]
        key_string = ":".join(key_parts)
        
        # Hash long keys to avoid Redis key length limits
        if len(key_string) > 200:
            key_string = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"{prefix}:{key_string}" if prefix else key_string
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """Get value from cache"""
        return cache.get(key, default)
    
    @staticmethod
    def set(key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """Set value in cache"""
        return cache.set(key, value, timeout)
    
    @staticmethod
    def delete(key: str) -> bool:
        """Delete key from cache"""
        return cache.delete(key)
    
    @staticmethod
    def delete_pattern(pattern: str) -> int:
        """Delete keys matching pattern (Redis only)"""
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            keys = redis_conn.keys(pattern)
            if keys:
                return redis_conn.delete(*keys)
            return 0
        except ImportError:
            # Fallback for non-Redis cache backends
            return 0
    
    @staticmethod
    def invalidate_menu_cache():
        """Invalidate all menu-related cache"""
        CacheService.delete_pattern(f"{CacheService.MENU_PREFIX}:*")
    
    @staticmethod
    def invalidate_analytics_cache():
        """Invalidate all analytics cache"""
        CacheService.delete_pattern(f"{CacheService.ANALYTICS_PREFIX}:*")
    
    @staticmethod
    def invalidate_reservation_cache():
        """Invalidate all reservation cache"""
        CacheService.delete_pattern(f"{CacheService.RESERVATION_PREFIX}:*")
    
    @staticmethod
    def invalidate_user_cache(user_id: int):
        """Invalidate cache for specific user"""
        CacheService.delete_pattern(f"{CacheService.USER_PREFIX}:{user_id}:*")


def cache_result(timeout: int = 300, prefix: str = "", key_func: Optional[Callable] = None):
    """
    Decorator to cache function results
    
    Args:
        timeout: Cache timeout in seconds
        prefix: Cache key prefix
        key_func: Function to generate cache key from args/kwargs
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = CacheService.make_key(*key_parts, prefix=prefix)
            
            # Try to get from cache
            result = CacheService.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            CacheService.set(cache_key, result, timeout)
            return result
        
        return wrapper
    return decorator


def cache_menu_items(timeout: int = CacheService.MENU_TIMEOUT):
    """Cache menu items"""
    return cache_result(timeout=timeout, prefix=CacheService.MENU_PREFIX)


def cache_analytics(timeout: int = CacheService.ANALYTICS_TIMEOUT):
    """Cache analytics data"""
    return cache_result(timeout=timeout, prefix=CacheService.ANALYTICS_PREFIX)


def cache_reservations(timeout: int = CacheService.RESERVATION_TIMEOUT):
    """Cache reservation data"""
    return cache_result(timeout=timeout, prefix=CacheService.RESERVATION_PREFIX)


def cache_user_data(timeout: int = CacheService.USER_TIMEOUT):
    """Cache user-specific data"""
    def key_func(*args, **kwargs):
        # Extract user_id from args or kwargs
        user_id = None
        if args and hasattr(args[0], 'user'):
            user_id = args[0].user.id
        elif 'user_id' in kwargs:
            user_id = kwargs['user_id']
        elif 'user' in kwargs and hasattr(kwargs['user'], 'id'):
            user_id = kwargs['user'].id
        
        key_parts = [str(user_id)] if user_id else []
        key_parts.extend(str(arg) for arg in args[1:])  # Skip first arg if it's self/request
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()) if k != 'user')
        
        return CacheService.make_key(*key_parts, prefix=CacheService.USER_PREFIX)
    
    return cache_result(timeout=timeout, key_func=key_func)


class CachedQuerySet:
    """Wrapper for caching QuerySet results"""
    
    def __init__(self, queryset, cache_key: str, timeout: int = 300):
        self.queryset = queryset
        self.cache_key = cache_key
        self.timeout = timeout
    
    def get_cached_result(self):
        """Get cached result or execute query"""
        result = CacheService.get(self.cache_key)
        if result is None:
            result = list(self.queryset)
            CacheService.set(self.cache_key, result, self.timeout)
        return result
    
    def invalidate(self):
        """Invalidate cached result"""
        CacheService.delete(self.cache_key)


# Cache warming functions
def warm_menu_cache():
    """Pre-populate menu cache with frequently accessed data"""
    from menu.models import MenuItem, Category
    
    # Cache all categories
    categories = list(Category.objects.all())
    CacheService.set(
        CacheService.make_key("all_categories", prefix=CacheService.MENU_PREFIX),
        categories,
        CacheService.MENU_TIMEOUT
    )
    
    # Cache available menu items
    available_items = list(MenuItem.objects.filter(available=True).select_related('category'))
    CacheService.set(
        CacheService.make_key("available_items", prefix=CacheService.MENU_PREFIX),
        available_items,
        CacheService.MENU_TIMEOUT
    )
    
    # Cache menu items by category
    for category in categories:
        category_items = list(MenuItem.objects.filter(
            category=category, available=True
        ))
        CacheService.set(
            CacheService.make_key("category_items", category.id, prefix=CacheService.MENU_PREFIX),
            category_items,
            CacheService.MENU_TIMEOUT
        )


def warm_analytics_cache():
    """Pre-populate analytics cache"""
    from analytics.services import AnalyticsService
    from datetime import date, timedelta
    
    # Cache dashboard metrics for common periods
    for days in [7, 30, 90]:
        metrics = AnalyticsService.get_dashboard_metrics(days)
        CacheService.set(
            CacheService.make_key("dashboard_metrics", days, prefix=CacheService.ANALYTICS_PREFIX),
            metrics,
            CacheService.ANALYTICS_TIMEOUT
        )
    
    # Cache recent daily summaries
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    from analytics.models import DailySummary
    summaries = list(DailySummary.objects.filter(
        date__range=[start_date, end_date]
    ).order_by('-date'))
    
    CacheService.set(
        CacheService.make_key("recent_summaries", prefix=CacheService.ANALYTICS_PREFIX),
        summaries,
        CacheService.ANALYTICS_TIMEOUT
    )


# Cache invalidation signals
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


@receiver([post_save, post_delete], sender='menu.MenuItem')
@receiver([post_save, post_delete], sender='menu.Category')
def invalidate_menu_cache(sender, **kwargs):
    """Invalidate menu cache when menu items or categories change"""
    CacheService.invalidate_menu_cache()


@receiver([post_save, post_delete], sender='orders.Order')
@receiver([post_save, post_delete], sender='payments.Payment')
def invalidate_analytics_cache(sender, **kwargs):
    """Invalidate analytics cache when orders or payments change"""
    CacheService.invalidate_analytics_cache()


@receiver([post_save, post_delete], sender='reservations.Reservation')
def invalidate_reservation_cache(sender, **kwargs):
    """Invalidate reservation cache when reservations change"""
    CacheService.invalidate_reservation_cache()
