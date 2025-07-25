from rest_framework import permissions


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Read: customer can only read their own orders; staff read all.
    Write: customer can create; only staff/admin can update status or delete.
    """

    def has_permission(self, request, view):
        # Anyone logged-in can list/create their own orders
        if view.action in ("list", "create"):
            return request.user and request.user.is_authenticated

        # Only staff can update or delete
        if view.action in ("update", "partial_update", "destroy"):
            return request.user and request.user.is_staff

        # detail view: read own or staff
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # SAFE methods: owner or staff
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_staff or obj.customer == request.user
        # non-safe methods: only staff
        return request.user.is_staff
