from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'items', views.InventoryItemViewSet)
router.register(r'categories', views.InventoryCategoryViewSet)
router.register(r'suppliers', views.SupplierViewSet)
router.register(r'movements', views.StockMovementViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
