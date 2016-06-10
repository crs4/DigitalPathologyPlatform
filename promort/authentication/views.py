try:
    import simplejson as json
except ImportError:
    import json

from django.contrib.auth import authenticate, login, logout

from rest_framework import status, views, permissions
from rest_framework.response import Response

from serializers import UserSerializer


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
