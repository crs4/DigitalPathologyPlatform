from rest_framework import permissions


class IsReviewManager(permissions.BasePermission):
    """
    Only superusers can CREATE and DELETE Review and ReviewStep objects
    """

    RESTRICTED_METHODS = ['POST', 'DELETE']

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated()):
            return False
        else:
            if request.method in self.RESTRICTED_METHODS:
                if request.user.is_superuser:
                    return True
                else:
                    return False
            else:
                return True
