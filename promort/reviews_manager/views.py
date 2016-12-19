try:
    import simplejson as json
except ImportError:
    import json
from datetime import datetime

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import MethodNotAllowed, NotFound

from django.contrib.auth.models import User

from django.db import IntegrityError

from view_templates.views import GenericListView

from reviews_manager.models import Review, ReviewStep, ROIsAnnotation, \
    ROIsAnnotationStep, ClinicalAnnotation, ClinicalAnnotationStep
from reviews_manager.serializers import ReviewSerializer,\
    ReviewDetailsSerializer, ReviewStepSerializer, ROIsAnnotationSerializer, \
    ROIsAnnotationStepSerializer, ROIsAnnotationDetailsSerializer, \
    ClinicalAnnotationSerializer, ClinicalAnnotationStepSerializer, ClinicalAnnotationDetailsSerializer
from reviews_manager.permissions import IsReviewManager

import logging
logger = logging.getLogger('promort')


class ReviewsList(GenericListView):
    model = Review
    model_serializer = ReviewSerializer
    permission_classes = (IsReviewManager,)

    def post(self, request, format=None):
        raise MethodNotAllowed


class ROIsAnnotationsList(GenericListView):
    model = ROIsAnnotation
    model_serializer = ROIsAnnotationSerializer
    permission_classes = (IsReviewManager,)

    def post(self, request, format=None):
        raise MethodNotAllowed


class ReviewsDetail(APIView):
    permission_classes = (IsReviewManager,)

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


class ROIsAnnotationsDetails(APIView):
    permission_classes = (IsReviewManager,)

    def _find_rois_annotation(self, case_id):
        try:
            return ROIsAnnotation.objects.filter(case=case_id)
        except ROIsAnnotation.DoesNotExist:
            raise NotFound('No ROIs annotations found for case ID \'%s\'' % case_id)

    def get(self, request, case, format=None):
        rois_annotations = self._find_rois_annotation(case)
        serializer = ROIsAnnotationSerializer(rois_annotations, many=True)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)


class ReviewDetail(APIView):
    permission_classes = (IsReviewManager,)

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
        reviewer = request.data.get('reviewer')
        if reviewer is None:
            return Response({
                'status': 'ERROR',
                'message': 'No reviewer specified'
            }, status=status.HTTP_400_BAD_REQUEST)

        review_data = {
            'reviewer': reviewer,
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


class ROIsAnnotationDetail(APIView):
    permission_classes = (IsReviewManager,)

    def _find_rois_annotation(self, case_id, reviewer):
        try:
            reviewer_obj = User.objects.filter(username=reviewer).first()
            return ROIsAnnotation.objects.get(case=case_id, reviewer=reviewer_obj)
        except User.DoesNotExist:
            raise NotFound('There is no reviewer with username \'%s\'' % reviewer)
        except ROIsAnnotation.DoesNotExist:
            raise NotFound('No ROIs annotations found assigned to reviewer \'%s\' for case \'%s\'' %
                           (case_id, reviewer))

    def get(self, request, case, reviewer, format=None):
        rois_annotation = self._find_rois_annotation(case, reviewer)
        serializer = ROIsAnnotationSerializer(rois_annotation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, case, reviewer, format=None):
        rois_annotation_data = {
            'reviewer': reviewer,
            'case': case
        }
        serializer = ROIsAnnotationSerializer(data=rois_annotation_data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError:
                return Response({
                    'status': 'ERROR',
                    'message': 'duplicated rois annotation for case %s assigned to reviewer %s' &
                               (case, reviewer)
                }, status=HTTP_409_CONFLICT)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, case, reviewer, format=None):
        rois_annotation = self._find_rois_annotation(case, reviewer)
        action = request.data.get('action')
        if action is not None:
            action = action.upper()
            if action == 'START':
                rois_annotation.start_date = datetime.now()
            elif action == 'FINISH':
                rois_annotation.completion_date = datetime.now()
            else:
                return Reponse({
                    'status': 'ERROR',
                    'message': '\'%s\' is not a valid action' % action
                }, status=status.HTTP_400_BAD_REQUEST)
            rois_annotation.save()
            serializer = ROIsAnnotationSerializer(rois_annotation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'ERROR',
                'message': 'Missing \'action\' field in request data'
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, case, reviewer, format=None):
        rois_annotation = self._find_rois_annotation(case, reviewer)
        try:
            rois_annotation.delete()
        except IntegrityError:
            return Response({
                'status': 'ERROR',
                'message': 'unable to complete delete operations, there are still references to this object'
            }, status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)

class ReviewStepDetail(APIView):
    permission_classes = (IsReviewManager,)

    def _find_review(self, case_id, review_type):
        try:
            return Review.objects.get(case=case_id, type=review_type.upper())
        except Review.DoesNotExist:
            raise NotFound('No review of type %s for case ID \'%s\'' % (review_type, case_id))

    def _find_review_step(self, case_id, review_type, slide_id):
        try:
            review = self._find_review(case_id, review_type)
            review_step = ReviewStep.objects.get(review=review, slide=slide_id)
            return review_step
        except ReviewStep.DoesNotExist:
            logger.error('No review step for slide %s for review type %s' % (slide_id, review_type))
            raise NotFound

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


class ROIsAnnotationStepDetail(APIView):
    permission_classes = (IsReviewManager,)

    def _find_rois_annotation(self, case_id, reviewer):
        try:
            reviewer_obj = User.objects.filter(username=reviewer).first()
            return ROIsAnnotation.objects.get(case=case_id, reviewer=reviewer_obj)
        except User.DoesNotExist:
            raise NotFound('There is no reviewer with username \'%s\'' % reviewer)
        except ROIsAnnotation.DoesNotExist:
            raise NotFound('No ROIs annotations found assigned to reviewer \'%s\' for case \'%s\'' %
                           (case_id, reviewer))

    def _find_rois_annotation_step(self, case_id, reviewer, slide_id):
        try:
            rois_annotation = self._find_rois_annotation(case_id, reviewer)
            annotation_step = ROIsAnnotationStep.objects.get(rois_annotation=rois_annotation, slide=slide_id)
            return annotation_step
        except ROIsAnnotationStep.DoesNotExist:
            raise NotFound('No ROIs annotation step for slide \'%s\'' % slide_id)

    def get(self, request, case, reviewer, slide, format=None):
        annotation_step = self._find_rois_annotation_step(case, reviewer, slide)
        serializer = ROIsAnnotationStepSerializer(annotation_step)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, case, reviewer, slide, format=None):
        rois_annotation = self._find_rois_annotation(case, reviewer)
        annotation_step_data = {
            'slide': slide,
            'rois_annotation': rois_annotation
        }
        serializer = ROIsAnnotationStepSerializer(data=annotation_step_data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError:
                return Response({
                    'status': 'ERROR',
                    'message': 'duplicated ROIs annotation step for slide \'%s\'' % slide
                }, status=status.HTTP_409_CONFLICT)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, case, reviewer, slide, format=None):
        annotation_step = self._find_rois_annotation_step(case, reviewer, slide)
        action = request.data.get('action')
        if action is not None:
            action = action.upper()
            if action == 'START':
                annotation_step.start_date = datetime.now()
            elif action == 'FINISH':
                annotation_step.completion_date = datetime.now()
            else:
                return Response({
                    'status': 'ERROR',
                    'message': '\'%s\' is not a valid action' % action
                }, status=status.HTTP_400_BAD_REQUEST)
            annotation_step.save()
            serializer = ROIsAnnotationStepSerializer(annotation_step)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'ERROR',
                'message': 'Missing \'action\' field in request data'
            }, status=status.HTTP_400_BAD_REQUEST)
