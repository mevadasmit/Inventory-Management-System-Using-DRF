from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
        Custom permission to only allow owners of an object to edit it.

        This permission allows read-only access for all users, but only the owner
        of an object can perform actions that modify the object.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user
