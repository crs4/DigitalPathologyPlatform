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
from reviews_manager.serializers import ROIsAnnotationSerializer, ROIsAnnotationStepSerializer, \
    ClinicalAnnotationSerializer, ClinicalAnnotationStepSerializer

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

    def get(self, request, format=None):
        rois_reviews, clinical_reviews = self._get_pending_reviews(request.user.username)
        rois_serializer = ROIsAnnotationSerializer(rois_reviews, many=True)
        clinical_serializer = ClinicalAnnotationSerializer(clinical_reviews, many=True)
        data = OrderedDict()
        # compose the worklist, keep clinical annotations only if ROIs annotation for the same case
        # was fully completed (and it was assigned to the current user)
        for c_ann in clinical_serializer.data:
            data[c_ann['case']] = c_ann
        for r_ann in rois_serializer.data:
            data[r_ann['case']] = r_ann
        return Response(data.values(), status=status.HTTP_200_OK)


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
