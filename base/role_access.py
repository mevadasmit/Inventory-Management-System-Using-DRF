from rest_framework.permissions import BasePermission

class RoleBasedPermission(BasePermission):
    """
    Allow access only to users with specific roles.
    """

    allowed_roles = []

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in view.allowed_roles