from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            (request.method in SAFE_METHODS and request.user.is_authenticated)
            or (request.user and request.user.is_staff)
        )


class ReadOnlyOrCreateIfAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS or (request.user and request.user.is_staff):
            return True
