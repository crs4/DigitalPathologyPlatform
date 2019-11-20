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

from collections import OrderedDict

from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from reviews_manager.models import ROIsAnnotation, ROIsAnnotationStep, \
    ClinicalAnnotation, ClinicalAnnotationStep
from questionnaires_manager.models import QuestionnaireRequest
from reviews_manager.serializers import ROIsAnnotationSerializer, ROIsAnnotationStepSerializer, \
    ClinicalAnnotationSerializer, ClinicalAnnotationStepSerializer
from questionnaires_manager.serializers import QuestionnaireRequestSerializer

import logging
logger = logging.getLogger('promort')


class UserWorkList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def _get_pending_reviews(self, username):
        rois_reviews = []
        clinical_reviews = []
        try:
            rois_reviews = ROIsAnnotation.objects.filter(
                reviewer=User.objects.get(username=username),
                completion_date=None
            ).order_by('case')
        except ROIsAnnotation.DoesNotExist:
            pass
        try:
            clinical_reviews = ClinicalAnnotation.objects.filter(
                reviewer=User.objects.get(username=username),
                completion_date=None
            ).order_by('case')
        except ClinicalAnnotation.DoesNotExist:
            pass
        return rois_reviews, clinical_reviews

    def _get_pending_questionnaire_requests(self, username):
        questionnaire_requests = []
        try:
            questionnaire_requests = QuestionnaireRequest.objects.filter(
                reviewer=User.objects.get(username=username),
                completion_date=None
            ).order_by('creation_date')
        except QuestionnaireRequest.DoesNotExist:
            pass
        return questionnaire_requests

    def get(self, request, format=None):
        rois_reviews, clinical_reviews = self._get_pending_reviews(request.user.username)
        rois_serializer = ROIsAnnotationSerializer(rois_reviews, many=True)
        clinical_serializer = ClinicalAnnotationSerializer(clinical_reviews, many=True)
        questionnaire_requests = self._get_pending_questionnaire_requests(request.user.username)
        questionnaire_serializer = QuestionnaireRequestSerializer(questionnaire_requests, many=True)
        data = OrderedDict()
        # compose the worklist, keep clinical annotations only if ROIs annotation for the same case
        # was fully completed (and it was assigned to the current user)
        for c_ann in clinical_serializer.data:
            data[c_ann['label']] = c_ann
        for r_ann in rois_serializer.data:
            data[r_ann['label']] = r_ann
        worklist = data.values()
        worklist.extend(questionnaire_serializer.data)
        return Response(worklist, status=status.HTTP_200_OK)


class UserWorklistROIsAnnotation(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def _get_rois_annotation_details(self, label):
        try:
            annotation = ROIsAnnotation.objects.get(label=label)
            return ROIsAnnotationStep.objects.filter(rois_annotation=annotation).order_by('slide')
        except ROIsAnnotation.DoesNotExist:
            raise NotFound('no ROIs annotation with label\'%s\'' % label)

    def get(self, request, label, format=None):
        annotation_steps = self._get_rois_annotation_details(label)
        serializer = ROIsAnnotationStepSerializer(annotation_steps, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserWorklistClinicalAnnotation(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def _get_clinical_annotation_details(self, label):
        try:
            annotation = ClinicalAnnotation.objects.get(label=label)
            return ClinicalAnnotationStep.objects.filter(clinical_annotation=annotation).order_by('slide')
        except ClinicalAnnotation.DoesNotExist:
            raise NotFound('no clinical annotation with label \'%s\'' % label)

    def get(self, request, label, format=None):
        annotation_steps = self._get_clinical_annotation_details(label)
        serializer = ClinicalAnnotationStepSerializer(annotation_steps, many=True,
                                                      context={'current_user': request.user.username})
        return Response(serializer.data, status=status.HTTP_200_OK)


class WorkListAdmin(APIView):
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, username, format=None):
        try:
            worklist = []
            user_obj = User.objects.get(username=username)
            rois_annotations = ROIsAnnotation.objects.filter(reviewer=user_obj)
            clinical_annotations = (ClinicalAnnotation.objects.filter(reviewer=user_obj))
            rois_annotations_serializer = ROIsAnnotationSerializer(rois_annotations, many=True)
            clinical_annotations_serializer = ClinicalAnnotationSerializer(clinical_annotations, many=True)
            worklist.extend(rois_annotations_serializer.data)
            worklist.extend(clinical_annotations_serializer.data)
            return Response(worklist, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            raise NotFound('no user with username %s' % username)
