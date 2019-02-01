#  Copyright (c) 2019, CRS4
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy of
#  this software and associated documentation files (the "Software"), to deal in
#  the Software without restriction, including without limitation the rights to
#  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
#  the Software, and to permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

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
