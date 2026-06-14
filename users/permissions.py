from rest_framework.permissions import BasePermission
from users.models import Admin


def has_role(*allowed_roles):
    class HasRole(BasePermission):
        def has_permission(self, request, view):
            user = request.user
            if not user.is_authenticated:
                return False
            if 'admin' in allowed_roles:
                try:
                    user.admin
                    return True
                except Admin.DoesNotExist:
                    pass
            if 'staff' in allowed_roles:
                return True
            return False
    return HasRole


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        try:
            user.admin
            return True
        except Admin.DoesNotExist:
            return False
