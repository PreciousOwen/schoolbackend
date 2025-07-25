from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import CorporateAccount, CorporateStaff, Invoice
from .serializers import (
    CorporateAccountSerializer,
    CorporateStaffSerializer,
    InvoiceSerializer
)
from .permissions import IsCorporateAdminOrReadOnly, IsInvoiceViewer

class CorporateAccountViewSet(viewsets.ModelViewSet):
    queryset           = CorporateAccount.objects.all()
    serializer_class   = CorporateAccountSerializer
    permission_classes = [IsCorporateAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields   = ['is_active']
    search_fields      = ['name']

class CorporateStaffViewSet(viewsets.ModelViewSet):
    queryset           = CorporateStaff.objects.select_related('user','corporate_account')
    serializer_class   = CorporateStaffSerializer
    permission_classes = [IsCorporateAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend]
    filterset_fields   = ['corporate_account', 'user']

class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admins and corporate-account owners can list/download invoices.
    """
    queryset           = Invoice.objects.select_related('corporate_account')
    serializer_class   = InvoiceSerializer
    permission_classes = [IsInvoiceViewer]
    filter_backends    = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields   = ['corporate_account', 'status']
    ordering_fields    = ['period_start']
