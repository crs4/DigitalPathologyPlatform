from rest_framework import permissions

from promort.settings import DEFAULT_GROUPS


class CanEnterGodMode(permissions.BasePermission):
    """
    Only specific users that belong to ODIN_MEMBERS group will be allowed
    to perform queries using Odin toolkit
    """

    RESTRICTED_METHODS = ['GET']

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated()):
            return False
        else:
            if request.method in self.RESTRICTED_METHODS:
                if request.user.groups.filter(
                        name__in=[DEFAULT_GROUPS['odin_members']['name']]
                ).exists():
                    return True
                else:
                    return False
            else:
                return False
