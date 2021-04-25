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

try:
    import simplejson as json
except ImportError:
    import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView

from .serializers import UserSerializer, GroupSerializer, GroupDetailsSerializer

from django.conf import settings

import logging
logger = logging.getLogger('promort')


class CheckUserView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        return Response({'username': request.user.username}, status=status.HTTP_200_OK)


class LoginView(APIView):

    def post(self, request, format=None):
        data = json.loads(request.body)

        username = data.get('username', None)
        password = data.get('password', None)

        account = authenticate(username=username, password=password)

        if account is not None:
            if account.is_active:
                login(request, account)

                serialized = UserSerializer(account)

                return Response(serialized.data,
                                status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': 'Unauthorized',
                    'message': 'This account has been disabled'
                }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({
                'status': 'Unauthorized',
                'message': 'Username/password combination invalid'
            }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        logout(request)

        return Response({}, status=status.HTTP_204_NO_CONTENT)


class ChangePasswordView(UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def update(self, request, format=None):
        user = request.user

        if not user.check_password(request.data.get('old_password')):
            return Response({
                'status': 'password_check_failed',
                'message': 'old password check failed'
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            user.set_password(request.data.get('new_password'))
            user.save()
            return Response({
                'status': 'success',
                'message': 'Password updated successfully'
            }, status=status.HTTP_200_OK)


class GroupListView(APIView):
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, format=None):
        groups = []
        for _, group in settings.DEFAULT_GROUPS.items():
            logger.debug('Loading data for group %s', group)
            groups.append(Group.objects.get(name=group['name']))
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GroupDetailsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, group, format=None):
        group = Group.objects.get(name=settings.DEFAULT_GROUPS[group]['name'])
        serializer = GroupDetailsSerializer(group)
        return Response(serializer.data, status=status.HTTP_200_OK)
