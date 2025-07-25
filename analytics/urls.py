# analytics/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AnalyticsEventViewSet, DashboardViewSet, ReportsViewSet, AnalyticsAPIViewSet
)

router = DefaultRouter()
router.register(r'events', AnalyticsEventViewSet, basename='analyticsevent')
router.register(r'dashboard', DashboardViewSet, basename='analytics-dashboard')
router.register(r'reports', ReportsViewSet, basename='reports')

# Add direct analytics endpoints for frontend compatibility
router.register(r'', AnalyticsAPIViewSet, basename='analytics')

urlpatterns = [
    path('', include(router.urls)),
]
