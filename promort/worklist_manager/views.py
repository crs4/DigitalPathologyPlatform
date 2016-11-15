try:
    import simplejson as json
except ImportError:
    import json

from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from slides_manager.models import Case
from reviews_manager.models import Review, ReviewStep
from reviews_manager.serializers import ReviewSerializer, ReviewStepSerializer

import logging
logger = logging.getLogger('promort')


class UserWorkList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def _get_pending_reviews(self, username):
        try:
            return Review.objects.filter(
                reviewer=User.objects.get(username=username),
                completion_date=None
            ).order_by('case')
        except Review.DoesNotExist:
            return []

    def get(self, request, format=None):
        reviews = self._get_pending_reviews(request.user.username)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserWorkListReview(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def _get_review_details(self, case_id, username):
        try:
            review = Review.objects.get(
                reviewer=User.objects.get(username=username),
                case=Case.objects.get(id=case_id)
            )
            return ReviewStep.objects.filter(review=review).order_by('slide')
        except Review.DoesNotExist:
            raise NotFound('No review assigned to user %s for case %s' % (username, case_id))
        except ReviewStep.DoesNotExist:
            return []

    def get(self, request, case, format=None):
        review_steps = self._get_review_details(case, request.user.username)
        serializer = ReviewStepSerializer(review_steps, many=True)
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
