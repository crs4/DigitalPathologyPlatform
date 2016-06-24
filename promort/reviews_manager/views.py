try:
    import simplejson as json
except ImportError:
    import json
from datetime import datetime

from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.exceptions import MethodNotAllowed, NotFound

from django.db import IntegrityError

from view_templates.views import GenericListView

from reviews_manager.models import Review, ReviewStep
from reviews_manager.serializers import ReviewSerializer,\
    ReviewDetailsSerializer, ReviewStepSerializer

import logging
logger = logging.getLogger('promort')


class ReviewsList(GenericListView):
    model = Review
    model_serializer = ReviewSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        raise MethodNotAllowed


class ReviewsDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def _find_review(self, case_id):
        try:
            return Review.objects.filter(case=case_id)
        except Review.DoesNotExist:
            raise NotFound('No reviews found for case ID \'%s\'' % case_id)

    def get(self, request, case, format=None):
        reviews = self._find_review(case)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)


class ReviewDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def _find_review(self, case_id, review_type):
        try:
            return Review.objects.get(case=case_id, type=review_type)
        except Review.DoesNotExist:
            raise NotFound('No review of type %s for case ID \'%s\'' % (review_type, case_id))

    def get(self, request, case, review_type, format=None):
        review = self._find_review(case, review_type.upper())
        serializer = ReviewDetailsSerializer(review)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    def post(self, request, case, review_type, format=None):
        review_data = {
            'reviewer': request.user.username,
            'case': case,
            'type': review_type.upper()
        }

        logger.debug('Serializing data %r -- Object class %r', review_data, Review)

        serializer = ReviewSerializer(data=review_data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError:
                return Response({
                    'status': 'ERROR',
                    'message': 'duplicated review of type %s for case %s' %
                               (serializer.data['review_type'], case)
                }, status=status.HTTP_409_CONFLICT)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, case, review_type, format=None):
        review = self._find_review(case, review_type.upper())
        action = request.data.get('action')
        if action is not None:
            action = action.upper()
            if action == 'START':
                review.start_date = datetime.now()
            elif action == 'FINISH':
                review.completion_date = datetime.now()
            else:
                return Response({
                    'status': 'ERROR',
                    'message': '\'%s\' is not a valid action' % action
                }, status=status.HTTP_400_BAD_REQUEST)
            review.save()
            serializer = ReviewSerializer(review)
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'ERROR',
                'message': 'Missing \'action\' field in request data'
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, case, review_type, format=None):
        review = self._find_review(case, review_type.upper())
        try:
            review.delete()
        except IntegrityError:
            return Response({
                'status': 'ERROR',
                'message': 'unable to complete delete operation, there are still references to this object'
            }, status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewStepDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def _find_review_step(self, case_id, review_type, slide_id):
        try:
            review = Review.objects.get(case=case_id, type=review_type)
            review_step = ReviewStep.objects.get(review=review, slide=slide_id)
            return review_step
        except Review.DoesNotExist:
            logger.error('No review for case %s of type %s' % (case_id, review_type))
            raise NotFound
        except ReviewStep.DoesNotExist:
            logger.error('No review step for slide %s for review type %s' % (slide_id, review_type))
            raise NotFound

    def _find_review(self, case_id, review_type):
        try:
            return Review.objects.get(case=case_id, type=review_type)
        except Review.DoesNotExist:
            raise NotFound('No review of type %s for case ID \'%s\'' % (review_type, case_id))

    def get(self, request, case, review_type, slide, format=None):
        review_step = self._find_review_step(case, review_type.upper(), slide)
        serializer = ReviewStepSerializer(review_step)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    def post(self, request, case, review_type, slide, format=None):
        review = self._find_review(case, review_type.upper())
        review_step_data = {
            'slide': slide,
            'review': review.id,
        }

        logger.debug('Serializing data %r -- Object class %r', review_step_data, ReviewStep)

        serializer = ReviewStepSerializer(data=review_step_data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError:
                return Response({
                    'status': 'ERROR',
                    'message': 'duplicated review step for review %s:%s' % (review.case.id, review.type)
                }, status=status.HTTP_409_CONFLICT)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, case, review_type, slide, format=None):
        review_step = self._find_review_step(case, review_type, slide)
        action = request.data.get('action')
        notes = request.data.get('notes')
        if action is not None:
            action = action.upper()
            if action == 'START':
                review_step.start_date = datetime.now()
            elif action == 'FINISH':
                review_step.completion_date = datetime.now()
            else:
                return Response({
                    'status': 'ERROR',
                    'message': '\'%s\' is not a valid action' % action
                }, status=status.HTTP_400_BAD_REQUEST)
            if notes:
                review_step.notes = notes
            review_step.save()
            serializer = ReviewStepSerializer(review_step)
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'ERROR',
                'message': 'Missing \'action\' field in request data'
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, case, review_type, slide, format=None):
        review_step = self._find_review_step(case, review_type, slide)
        try:
            review_step.delete()
        except IntegrityError:
            return Response({
                'status': 'ERROR',
                'message': 'unable to complete delete operation, there are still references to this object'
            }, status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)
