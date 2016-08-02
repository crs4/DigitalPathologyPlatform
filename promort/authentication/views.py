try:
    import simplejson as json
except ImportError:
    import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group

from rest_framework import status, views, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from serializers import UserSerializer, GroupSerializer, GroupDetailsSerializer

from promort.settings import DEFAULT_GROUPS

import logging
logger = logging.getLogger('promort')


class CheckUserView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        return Response(status=status.HTTP_204_NO_CONTENT)


class LoginView(views.APIView):

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


class LogoutView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        logout(request)

        return Response({}, status=status.HTTP_204_NO_CONTENT)


class GroupListView(APIView):
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, format=None):
        groups = []
        for _, group in DEFAULT_GROUPS.iteritems():
            logger.debug('Loading data for group %s', group)
            groups.append(Group.objects.get(name=group['name']))
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GroupDetailsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, group, format=None):
        group = Group.objects.get(name=DEFAULT_GROUPS[group]['name'])
        serializer = GroupDetailsSerializer(group)
        return Response(serializer.data, status=status.HTTP_200_OK)
