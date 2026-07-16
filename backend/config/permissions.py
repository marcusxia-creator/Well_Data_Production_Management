from rest_framework.permissions import BasePermission

VIEWER_GROUP_NAME = "Dashboard and Production Viewer"


def is_restricted_viewer(user):
    return bool(user and user.is_authenticated and not user.is_superuser and user.groups.filter(name=VIEWER_GROUP_NAME).exists())


class IsNotRestrictedViewer(BasePermission):
    message = "This account only has access to the Well Dashboard and Production Modules."

    def has_permission(self, request, view):
        return not is_restricted_viewer(request.user)
