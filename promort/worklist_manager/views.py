try:
    import simplejson as json
except ImportError:
    import json

from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

from reviews_manager.models import Review
from reviews_manager.serializers import ReviewSerializer

import logging
logger = logging.getLogger('promort')


class UserWorkList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def _get_pending_reviews(self, username):
        try:
            return Review.objects.filter(reviewer=username,
                                         completion_date=None)
        except Review.DoesNotExist:
            return []

    def get(self, request, format=None):
        reviews = self._get_pending_reviews(request.user.username)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WorkListAdmin(APIView):
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, username, format=None):
        try:
            reviews = Review.objects.filter(reviewer=username)
        except Review.DoesNotExist:
            reviews = []
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
