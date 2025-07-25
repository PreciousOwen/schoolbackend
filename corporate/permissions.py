from rest_framework import permissions

class IsCorporateAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # only staff (is_staff) can mutate accounts & staff
        if view.action in ('create','update','partial_update','destroy'):
            return request.user and request.user.is_staff
        return True  # anyone authenticated can list/view

class IsInvoiceViewer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
