from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from odin.permissions import CanEnterGodMode


class CheckAccessPrivileges(APIView):
    permission_classes = (CanEnterGodMode,)

    def get(self, request, format=None):
        return Response(status=status.HTTP_204_NO_CONTENT)
