from django.conf import settings
from rest_framework.permissions import BasePermission


class IsAdminOrDevOpen(BasePermission):
    """
    Require admin user when ADMIN_AUTH_REQUIRED=True.
    Keep local/dev open when ADMIN_AUTH_REQUIRED=False.
    """

    def has_permission(self, request, view):
        if not getattr(settings, 'ADMIN_AUTH_REQUIRED', False):
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)

