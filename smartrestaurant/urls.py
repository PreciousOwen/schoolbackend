# smartrestaurant/urls.py

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.routers import DefaultRouter

from menu.views import CategoryViewSet, MenuItemViewSet
from orders.views import OrderViewSet, KitchenQueueViewSet, OrderAnalyticsViewSet
from reservations.views import (
    ReservationViewSet, TableViewSet, WaitlistViewSet, ReservationAnalyticsViewSet
)
from corporate.views import (
    CorporateAccountViewSet,
    CorporateStaffViewSet,
    InvoiceViewSet
)
from .health import health_check

# ─── DRF Router ────────────────────────────────────────────────────────────────
router = DefaultRouter()
router.register(r"menu/categories", CategoryViewSet, basename="category")
router.register(r"menu/items", MenuItemViewSet, basename="menuitem")
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"kitchen/queue", KitchenQueueViewSet, basename="kitchenqueue")
router.register(r"analytics/orders", OrderAnalyticsViewSet, basename="orderanalytics")
router.register(r"tables", TableViewSet, basename="table")
router.register(r"reservations", ReservationViewSet, basename="reservation")
router.register(r"waitlist", WaitlistViewSet, basename="waitlist")
router.register(r"analytics/reservations", ReservationAnalyticsViewSet, basename="reservationanalytics")
router.register(r'corporate/accounts', CorporateAccountViewSet, basename='corpaccount')
router.register(r'corporate/staff',    CorporateStaffViewSet,    basename='corpstaff')
router.register(r'corporate/invoices', InvoiceViewSet,    basename='invoice')



# ─── API ROOT ──────────────────────────────────────────────────────────────────
@api_view(["GET"])
def api_root(request, format=None):
    """
    Discoverable entry point for your API.
    GET /api/ returns links to login, profile, categories, and menu items.
    """
    return Response(
        {
            "login": reverse("login", request=request, format=format),
            "profile": reverse("profile", request=request, format=format),
            "categories": reverse("category-list", request=request, format=format),
            "menu_items": reverse("menuitem-list", request=request, format=format),
        }
    )


# ─── URL PATTERNS ──────────────────────────────────────────────────────────────
urlpatterns = [
    # Admin site
    path("admin/", admin.site.urls),
    # Health check
    path("api/health/", health_check, name="health-check"),
    # API root (GET /api/)
    path("api/", api_root, name="api-root"),
    # Accounts endpoints (/api/accounts/login/, /api/accounts/profile/)
    path("api/accounts/", include("accounts.urls")),
    # Payment endpoints
    path("api/payments/", include("payments.urls")),
    # Notification endpoints
    path("api/notifications/", include("notifications.urls")),
    # Analytics endpoints
    path("api/analytics/", include("analytics.urls")),
    # Inventory endpoints
    path("api/inventory/", include("inventory.urls")),
    # Menu endpoints via DRF router
    path("api/", include(router.urls)),
    # OpenAPI schema (raw JSON/YAML)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Swagger UI at /api/docs/
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
