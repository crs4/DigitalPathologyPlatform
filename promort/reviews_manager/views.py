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

from datetime import datetime
from uuid import uuid4

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


class ROIsAnnotationCreation(APIView):
    permission_classes = (IsReviewManager,)

    def post(self, request, case, reviewer, format=None):
        rois_annotation_data = {
            'reviewer': reviewer,
            'case': case,
            'label': uuid4().hex
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


class ROIsAnnotationDetail(APIView):
    permission_classes = (IsReviewManager,)

    def _find_rois_annotation(self, label):
        try:
            return ROIsAnnotation.objects.get(label=label)
        except ROIsAnnotation.DoesNotExist:
            raise NotFound('No ROIs annotations with label \'%s\'', label)

    def get(self, request, label, format=None):
        rois_annotation = self._find_rois_annotation(label)
        serializer = ROIsAnnotationDetailsSerializer(rois_annotation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, label, format=None):
        rois_annotation = self._find_rois_annotation(label)
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

    def delete(self, request, label, format=None):
        rois_annotation = self._find_rois_annotation(label)
        try:
            rois_annotation.delete()
        except IntegrityError:
            return Response({
                'status': 'ERROR',
                'message': 'unable to complete delete operations, there are still references to this object'
            }, status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClinicalAnnotationCreation(APIView):
    permission_classes = (IsReviewManager,)

    def _get_rois_review_label(self, rois_review_id, reviewer):
        try:
            rois_review_obj = ROIsAnnotation.objects.get(id=rois_review_id)
            if rois_review_obj.reviewer.username == reviewer:
                return rois_review_obj.label
            else:
                return uuid4().hex
        except ROIsAnnotation.DoesNotExist:
            raise NotFound('No ROIs review with ID \'%s\'' % rois_review_id)

    def post(self, request, case, reviewer, rois_review, format=None):
        clinical_annotation_data = {
            'label': self._get_rois_review_label(rois_review, reviewer),
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


class ClinicalAnnotationDetail(APIView):
    permission_classes = (IsReviewManager,)

    def _find_clinical_annotation(self, label):
        try:
            return ClinicalAnnotation.objects.get(label=label)
        except ClinicalAnnotation.DoesNotExist:
            raise NotFound('No clinical annotation found with label \'%s\'' % label)

    def get(self, request, label, format=None):
        clinical_annotation = self._find_clinical_annotation(label)
        serializer = ClinicalAnnotationDetailsSerializer(clinical_annotation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, label, format=None):
        clinical_annotation = self._find_clinical_annotation(label)
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

    def delete(self, request, label, format=None):
        clinical_annotation = self._find_clinical_annotation(label)
        try:
            clinical_annotation.delete()
        except IntegrityError:
            return Response({
                'status': 'ERROR',
                'message': 'unable to complete delete operation, there are still references to this object'
            }, status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ROIsAnnotationStepCreation(APIView):
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

    def _get_step_label(self, rois_annotation, slide):
        slide_index = slide.split('-')[-1]
        return '%s-%s' % (rois_annotation.label, slide_index)

    def post(self, request, case, reviewer, slide, format=None):
        rois_annotation = self._find_rois_annotation(case, reviewer)
        annotation_step_data = {
            'label': self._get_step_label(rois_annotation, slide),
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


class ROIsAnnotationStepReopen(APIView):
    permission_classes = (IsReviewManager,)

    def _find_rois_annotation_step(self, label):
        try:
            annotation_step = ROIsAnnotationStep.objects.get(label=label)
            return annotation_step
        except ROIsAnnotationStep.DoesNotExist:
            raise NotFound('No ROIs annotation step with label \'%s\'' % label)

    def put(self, request, label, format=None):
        annotation_step = self._find_rois_annotation_step(label)
        try:
            annotation_step.reopen()
        except IntegrityError:
            return Response(
                {
                    'status': 'ERROR',
                    'message': 'ROIs annotation step %s can\'t be cancelled due to integrity error' % label
                }, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class ROIsAnnotationStepDetail(APIView):
    permission_classes = (IsReviewManager,)

    def _find_rois_annotation_step(self, label):
        try:
            annotation_step = ROIsAnnotationStep.objects.get(label=label)
            return annotation_step
        except ROIsAnnotationStep.DoesNotExist:
            raise NotFound('No ROIs annotation step with label \'%s\'' % label)

    def get(self, request, label, format=None):
        annotation_step = self._find_rois_annotation_step(label)
        serializer = ROIsAnnotationStepDetailsSerializer(annotation_step)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, label, format=None):
        annotation_step = self._find_rois_annotation_step(label)
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
                    }, status=status.HTTP_400_BAD_REQUEST)
            elif action == 'FINISH':
                if not annotation_step.is_completed():
                    annotation_step.completion_date = datetime.now()
                else:
                    return Response({
                        'status': 'ERROR',
                        'message': 'ROIs annotation step can\'t be closed'
                    }, status=status.HTTP_400_BAD_REQUEST)
            elif action == 'START_AND_FINISH':
                if not annotation_step.is_started():
                    annotation_step.start_date = datetime.now()
                if not annotation_step.is_completed():
                    annotation_step.completion_date = datetime.now()
            else:
                return Response({
                    'status': 'ERROR',
                    'message': '\'%s\' is not a valid action' % action
                }, status=status.HTTP_400_BAD_REQUEST)
            annotation_step.save()
            # after closing an annotation step, also check if ROIs annotation can be closed
            rois_annotation_closed = False
            if action in ('FINISH', 'START_AND_FINISH'):
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

    def delete(self, request, label, format=None):
        annotation_step = self._find_rois_annotation_step(label)
        try:
            annotation_step.delete()
        except IntegrityError:
            return Response({
                'status': 'ERROR',
                'message': 'unable to complete delete operation, there are still references to this object'
            }, status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClinicalAnnotationStepsList(APIView):
    permission_classes = (IsReviewManager,)

    def _find_rois_annotation_step(self, annotation_step_label):
        try:
            return ROIsAnnotationStep.objects.get(label=annotation_step_label)
        except ROIsAnnotationStep.DoesNotExist:
            raise NotFound('No ROIs annotation step with label %s' % annotation_step_label)

    def _apply_action(self, step, action, notes):
        clinical_annotation = step.clinical_annotation
        if action in ('START', 'START_AND_FINISH'):
            if not clinical_annotation.is_started():
                clinical_annotation.start_date = datetime.now()
                clinical_annotation.save()
        if action == 'START':
            if not step.is_started():
                step.start_date = datetime.now()
        elif action == 'FINISH':
            if not step.is_completed():
                step.completion_date = datetime.now()
                step.notes = notes
        elif action == 'START_AND_FINISH':
            if not step.is_started():
                step.start_date = datetime.now()
            if not step.is_completed():
                step.completion_date = datetime.now()
                step.notes = notes
        step.save()
        if action in ('FINISH', 'START_AND_FINISH'):
            if clinical_annotation.can_be_closed() and not clinical_annotation.is_completed():
                clinical_annotation.completion_date = datetime.now()
                clinical_annotation.save()

    def get(self, request, label, format=None):
        rois_annotation_step = self._find_rois_annotation_step(label)
        clinical_steps = rois_annotation_step.clinical_annotation_steps.all()
        serializer = ClinicalAnnotationStepSerializer(clinical_steps, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, label, format=None):
        rois_annotation_step = self._find_rois_annotation_step(label)
        clinical_steps = rois_annotation_step.clinical_annotation_steps.all()
        action = request.data.get('action')
        notes = request.data.get('notes')
        if action is not None:
            action = action.upper()
            if action in ('START', 'FINISH', 'START_AND_FINISH'):
                for step in clinical_steps:
                    self._apply_action(step, action, notes)
                serializer = ClinicalAnnotationStepSerializer(clinical_steps, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': 'ERROR',
                    'message': '%s is not a valid action' % action
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'status': 'ERROR',
                'message': 'missing \'action\' field in request data'
            }, status=status.HTTP_400_BAD_REQUEST)


class ClinicalAnnotationStepCreation(APIView):
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

    def _find_rois_review_step(self, rois_review_id, slide_id):
        try:
            return ROIsAnnotationStep.objects.get(rois_annotation=rois_review_id, slide=slide_id)
        except ROIsAnnotationStep.DoesNotExist:
            raise NotFound('No ROIs annotation step for ROIs Annotation %s related to slide %s' %
                           (rois_review_id, slide_id))

    def _find_clinical_annotation_step(self, case_id, reviewer, rois_review_id, slide_id):
        try:
            clinical_annotation = self._find_clinical_annotation(case_id, reviewer, rois_review_id)
            annotation_step = ClinicalAnnotationStep.objects.get(clinical_annotation=clinical_annotation,
                                                                 slide=slide_id)
            return annotation_step
        except ClinicalAnnotationStep.DoesNotExist:
            raise NotFound('No clinical annotation step for slide \'%s\'' % slide_id)

    def _get_step_label(self, clinical_annotation, slide):
        slide_index = slide.split('-')[-1]
        return '%s-%s' % (clinical_annotation.label, slide_index)

    def post(self, request, case, reviewer, rois_review, slide, format=None):
        clinical_annotation = self._find_clinical_annotation(case, reviewer, rois_review)
        rois_annotation_step = self._find_rois_review_step(rois_review, slide)
        annotation_step_data = {
            'label': self._get_step_label(clinical_annotation, slide),
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


class ClinicalAnnotationStepDetail(APIView):
    permission_classes = (IsReviewManager,)

    def _find_clinical_annotation_step(self, label):
        try:
            annotation_step = ClinicalAnnotationStep.objects.get(label=label)
            return annotation_step
        except ClinicalAnnotationStep.DoesNotExist:
            raise NotFound('No clinical annotation step with label \'%s\'' % label)

    def get(self, request, label, format=None):
        annotation_step = self._find_clinical_annotation_step(label)
        serializer = ClinicalAnnotationStepSerializer(annotation_step)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, label, format=None):
        annotation_step = self._find_clinical_annotation_step(label)
        action = request.data.get('action')
        if action is not None:
            action = action.upper()
            # check if annotation_step can really be started
            if action in ('START', 'START_AND_FINISH'):
                if not annotation_step.can_be_started():
                    return Response({
                        'status': 'ERROR',
                        'message': 'clinical annotation step can\'t be started because ROIs annotation is not completed'
                    }, status=status.HTTP_403_FORBIDDEN)
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
                    if not request.data.get('rejected') is None:
                        annotation_step.rejected = request.data.get('rejected')
                    annotation_step.rejection_reason = request.data.get('rejection_reason')
                else:
                    return Response({
                        'status': 'ERROR',
                        'message': 'clinical annotation step can\'t be closed'
                    }, status=status.HTTP_409_CONFLICT)
            elif action == 'START_AND_FINISH':
                if not annotation_step.is_started():
                    annotation_step.start_date = datetime.now()
                if not annotation_step.is_completed():
                    annotation_step.completion_date = datetime.now()
                    annotation_step.notes = request.data.get('notes')
                    if not request.data.get('rejected') is None:
                        annotation_step.rejected = request.data.get('rejected')
                    annotation_step.rejection_reason = request.data.get('rejection_reason')
            else:
                return Response({
                    'status': 'ERROR',
                    'message': '\'%s\' is not a valid action' % action
                }, status=status.HTTP_400_BAD_REQUEST)
            annotation_step.save()
            clinical_annotation_closed = False
            if action in ('FINISH', 'START_AND_FINISH'):
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

    def delete(self, request, label, format=None):
        annotation_step = self._find_clinical_annotation_step(label)
        try:
            annotation_step.delete()
        except IntegrityError:
            return Response({
                'status': 'ERROR',
                'message': 'unable to complete delete operation, there are still references to this object'
            }, status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)
