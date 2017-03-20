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

from reviews_manager.models import ROIsAnnotation, ROIsAnnotationStep, ClinicalAnnotation, \
    ClinicalAnnotationStep
from reviews_manager.serializers import ROIsAnnotationSerializer, ROIsAnnotationStepSerializer, \
    ROIsAnnotationDetailsSerializer, ROIsAnnotationStepDetailsSerializer, ClinicalAnnotationSerializer, \
    ClinicalAnnotationStepSerializer, ClinicalAnnotationDetailsSerializer
from reviews_manager.permissions import IsReviewManager

import logging
logger = logging.getLogger('promort')


class ROIsAnnotationsList(GenericListView):
    model = ROIsAnnotation
    model_serializer = ROIsAnnotationSerializer
    permission_classes = (IsReviewManager,)

    def post(self, request, format=None):
        raise MethodNotAllowed


class ClinicalAnnotationsList(GenericListView):
    model = ClinicalAnnotation
    model_serializer = ClinicalAnnotationSerializer
    permission_classes = (IsReviewManager,)

    def post(self, request, format=None):
        raise MethodNotAllowed


class ROIsAnnotationsDetail(APIView):
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


class ClinicalAnnotationsDetail(APIView):
    permission_classes = (IsReviewManager,)

    def _find_clinical_annotation(self, case_id):
        try:
            return ClinicalAnnotation.objects.filter(case=case_id)
        except ClinicalAnnotation.DoesNotExist:
            raise NotFound('No clinical annotations found for case ID \'%s\'' % case_id)

    def get(self, request, case, format=None):
        clinical_annotations = self._find_clinical_annotation(case)
        serializer = ClinicalAnnotationSerializer(clinical_annotations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ROIsAnnotationDetail(APIView):
    permission_classes = (IsReviewManager,)

    def _find_rois_annotation(self, case_id, reviewer):
        try:
            reviewer_obj = User.objects.get(username=reviewer)
            return ROIsAnnotation.objects.get(case=case_id, reviewer=reviewer_obj)
        except User.DoesNotExist:
            raise NotFound('There is no reviewer with username \'%s\'' % reviewer)
        except ROIsAnnotation.DoesNotExist:
            raise NotFound('No ROIs annotations found assigned to reviewer \'%s\' for case \'%s\'' %
                           (reviewer, case_id))

    def get(self, request, case, reviewer, format=None):
        rois_annotation = self._find_rois_annotation(case, reviewer)
        serializer = ROIsAnnotationDetailsSerializer(rois_annotation)
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
                    'message': 'duplicated rois annotation for case %s assigned to reviewer %s' %
                               (case, reviewer)
                }, status=status.HTTP_409_CONFLICT)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, case, reviewer, format=None):
        rois_annotation = self._find_rois_annotation(case, reviewer)
        action = request.data.get('action')
        if action is not None:
            action = action.upper()
            if action == 'START':
                if not rois_annotation.is_started():
                    rois_annotation.start_date = datetime.now()
                else:
                    return Response({
                        'status': 'ERROR',
                        'message': 'ROIs annotation can\'t be started'
                    }, status=status.HTTP_409_CONFLICT)
            elif action == 'FINISH':
                if rois_annotation.can_be_closed() and not rois_annotation.is_completed():
                    rois_annotation.completion_date = datetime.now()
                else:
                    return Response({
                        'status': 'ERROR',
                        'message': 'ROIs annotation can\'t be closed'
                    }, status=status.HTTP_409_CONFLICT)
            else:
                return Response({
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


class ClinicalAnnotationDetail(APIView):
    permission_classes = (IsReviewManager,)

    def _find_clinical_annotation(self, case_id, reviewer, rois_review_id):
        try:
            reviewer_obj = User.objects.get(username=reviewer)
            return ClinicalAnnotation.objects.get(case=case_id, reviewer=reviewer_obj,
                                                  rois_review=rois_review_id)
        except User.DoesNotExist:
            raise NotFound('There is no reviewer with username \'%s\'' % reviewer)
        except ClinicalAnnotation.DoesNotExist:
            raise NotFound('No clinical annotation found assigned to reviewer \'%s\' for case \'%s\'' %
                           (reviewer, case_id))

    def get(self, request, case, reviewer, rois_review, format=None):
        clinical_annotation = self._find_clinical_annotation(case, reviewer, rois_review)
        serializer = ClinicalAnnotationDetailsSerializer(clinical_annotation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, case, reviewer, rois_review, format=None):
        clinical_annotation_data = {
            'reviewer': reviewer,
            'case': case,
            'rois_review': rois_review
        }
        serializer = ClinicalAnnotationSerializer(data=clinical_annotation_data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError:
                return Response({
                    'status': 'ERROR',
                    'message': 'duplicated clinical annotation for case %s assignet to reviewer %s' %
                               (case, reviewer)
                }, status=status.HTTP_409_CONFLICT)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, case, reviewer, rois_review, format=None):
        clinical_annotation = self._find_clinical_annotation(case, reviewer, rois_review)
        action = request.data.get('action')
        if action is not None:
            action = action.upper()
            if action == 'START':
                if not clinical_annotation.is_started():
                    clinical_annotation.start_date = datetime.now()
                else:
                    return Response({
                        'status': 'ERROR',
                        'message': 'clinical annotation can\'t be started'
                    }, status=status.HTTP_409_CONFLICT)
            elif action == 'FINISH':
                if clinical_annotation.can_be_closed() and not clinical_annotation.is_completed():
                    clinical_annotation.completion_date = datetime.now()
                else:
                    return Response({
                        'status': 'ERROR',
                        'message': 'clinical annotation can\'t be closed'
                    }, status=status.HTTP_409_CONFLICT)
            else:
                return Response({
                    'status': 'ERROR',
                    'message': '\'%s\' is not a valid action' % action
                }, status=status.HTTP_400_BAD_REQUEST)
            clinical_annotation.save()
            serializer = ClinicalAnnotationSerializer(clinical_annotation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'ERROR',
                'message': 'Missing \'action\' field in request data'
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, case, reviewer, rois_review, format=None):
        clinical_annotation = self._find_clinical_annotation(case, reviewer, rois_review)
        try:
            clinical_annotation.delete()
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
        serializer = ROIsAnnotationStepDetailsSerializer(annotation_step)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, case, reviewer, slide, format=None):
        rois_annotation = self._find_rois_annotation(case, reviewer)
        annotation_step_data = {
            'slide': slide,
            'rois_annotation': rois_annotation.id
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
                if not annotation_step.is_started():
                    annotation_step.start_date = datetime.now()
                else:
                    return Response({
                        'status': 'ERROR',
                        'message': 'ROIs annotation step can\'t be started'
                    }, status=status.HTTP_409_CONFLICT)
            elif action == 'FINISH':
                if not annotation_step.is_completed():
                    annotation_step.completion_date = datetime.now()
                else:
                    return Response({
                        'status': 'ERROR',
                        'message': 'ROIs annotation step can\'t be closed'
                    }, status=status.HTTP_409_CONFLICT)
            else:
                return Response({
                    'status': 'ERROR',
                    'message': '\'%s\' is not a valid action' % action
                }, status=status.HTTP_400_BAD_REQUEST)
            annotation_step.save()
            # after closing an annotation step, also check if ROIs annotation can be closed
            rois_annotation_closed = False
            if action == 'FINISH':
                rois_annotation = annotation_step.rois_annotation
                if rois_annotation.can_be_closed():
                    rois_annotation.completion_date = datetime.now()
                    rois_annotation.save()
                    rois_annotation_closed = True
            serializer = ROIsAnnotationStepSerializer(annotation_step)
            return Response({
                'rois_annotation_step': serializer.data,
                'rois_annotation_closed': rois_annotation_closed
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'ERROR',
                'message': 'missing \'action\' field in request data'
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, case, reviewer, slide, format=None):
        annotation_step = self._find_rois_annotation_step(case, reviewer, slide)
        try:
            annotation_step.delete()
        except IntegrityError:
            return Response({
                'status': 'ERROR',
                'message': 'unable to complete delete operation, there are still references to this object'
            }, status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClinicalAnnotationStepDetail(APIView):
    permission_classes = (IsReviewManager,)

    def _find_clinical_annotation(self, case_id, reviewer, rois_review_id):
        try:
            reviewer_obj = User.objects.get(username=reviewer)
            return ClinicalAnnotation.objects.get(case=case_id, reviewer=reviewer_obj,
                                                  rois_review=rois_review_id)
        except User.DoesNotExist:
            raise NotFound('There is no reviewer with userna \'%s\'' % reviewer)
        except ClinicalAnnotation.DoesNotExist:
            raise NotFound('No clinical annotation found assigned to reviewer \'%s\' for case \'%s\'' %
                           (reviewer, case_id))

    def _find_clinical_annotation_step(self, case_id, reviewer, rois_review_id, slide_id):
        try:
            clinical_annotation = self._find_clinical_annotation(case_id, reviewer, rois_review_id)
            annotation_step = ClinicalAnnotationStep.objects.get(clinical_annotation=clinical_annotation,
                                                                 slide=slide_id)
            return annotation_step
        except ClinicalAnnotationStep.DoesNotExist:
            raise NotFound('No clinical annotation step for slide \'%s\'' % slide_id)

    def _find_rois_review_step(self, rois_review_id, slide_id):
        try:
            return ROIsAnnotationStep.objects.get(rois_annotation=rois_review_id, slide=slide_id)
        except ROIsAnnotationStep.DoesNotExist:
            raise NotFound('No ROIs annotation step for ROIs Annotation %s related to slide %s' %
                           (rois_review_id, slide_id))

    def get(self, request, case, reviewer, rois_review, slide, format=None):
        annotation_step = self._find_clinical_annotation_step(case, reviewer, rois_review, slide)
        serializer = ClinicalAnnotationStepSerializer(annotation_step)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, case, reviewer, rois_review, slide, format=None):
        clinical_annotation = self._find_clinical_annotation(case, reviewer, rois_review)
        rois_annotation_step = self._find_rois_review_step(rois_review, slide)
        annotation_step_data = {
            'slide': slide,
            'clinical_annotation': clinical_annotation.id,
            'rois_review_step': rois_annotation_step.id
        }
        serializer = ClinicalAnnotationStepSerializer(data=annotation_step_data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError:
                return Response({
                    'status': 'ERROR',
                    'message': 'duplicated clinical annotation step for slide \'%s\'' % slide
                }, status=status.HTTP_409_CONFLICT)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, case, reviewer, rois_review, slide, format=None):
        annotation_step = self._find_clinical_annotation_step(case, reviewer, rois_review, slide)
        action = request.data.get('action')
        if action is not None:
            action = action.upper()
            if action == 'START':
                if not annotation_step.is_started():
                    annotation_step.start_date = datetime.now()
                else:
                    return Response({
                        'status': 'ERROR',
                        'message': 'clinical annotation step can\'t be started'
                    }, status=status.HTTP_409_CONFLICT)
            elif action == 'FINISH':
                if not annotation_step.is_completed():
                    annotation_step.completion_date = datetime.now()
                    annotation_step.notes = request.data.get('notes')
                else:
                    return Response({
                        'status': 'ERROR',
                        'message': 'clinical annotation step can\'t be closed'
                    }, status=status.HTTP_409_CONFLICT)
            else:
                return Response({
                    'status': 'ERROR',
                    'message': '\'%s\' is not a valid action' % action
                }, status=status.HTTP_400_BAD_REQUEST)
            annotation_step.save()
            clinical_annotation_closed = False
            if action == 'FINISH':
                clinical_annotation = annotation_step.clinical_annotation
                if clinical_annotation.can_be_closed() and not clinical_annotation.is_completed():
                    clinical_annotation.completion_date = datetime.now()
                    clinical_annotation.save()
                    clinical_annotation_closed = True
            serializer = ClinicalAnnotationStepSerializer(annotation_step)
            return Response({
                'clinical_annotation_step': serializer.data,
                'clinical_annotation_closed': clinical_annotation_closed
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'ERROR',
                'message': 'missing \'action\' field in requesta data'
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, case, reviewer, rois_review, slide, format=None):
        annotation_step = self._find_clinical_annotation_step(case, reviewer, rois_review, slide)
        try:
            annotation_step.delete()
        except IntegrityError:
            return Response({
                'status': 'ERROR',
                'message': 'unable to complete delete operation, there are still references to this object'
            }, status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)
