from rest_framework import permissions


class IsAppCreatorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        # so, we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to the owner of an app.
        # Convert obj.owner str obj because request.user.id is a str type while obj.owner is a UUID type
        return str(obj.owner) == str(request.user.id)
