from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from django.contrib.auth.models import User
from django.db import IntegrityError

from view_templates.views import GenericDetailView, GenericListView

from slides_manager.models import Case, Slide, SlideQualityControl
from slides_manager.serializers import CaseSerializer, CaseDetailedSerializer,\
    SlideSerializer, SlideDetailSerializer, SlideQualityControlSerializer
from reviews_manager.models import ROIsAnnotation, ROIsAnnotationStep

import logging
logger = logging.getLogger('promort')


class CaseList(GenericListView):
    model = Case
    model_serializer = CaseSerializer
    permission_classes = (permissions.IsAuthenticated,)


class CaseDetail(GenericDetailView):
    model = Case
    model_serializer = CaseDetailedSerializer
    permission_classes = (permissions.IsAuthenticated,)


class SlideList(GenericListView):
    model = Slide
    model_serializer = SlideSerializer
    permission_classes = (permissions.IsAuthenticated,)


class SlideDetail(GenericDetailView):
    model = Slide
    model_serializer = SlideDetailSerializer
    permission_classes = (permissions.IsAuthenticated,)


class SlideQualityControlDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def _find_rois_annotation_step(self, label):
        try:
            return ROIsAnnotationStep.objects.get(label=label)
        except ROIsAnnotationStep.DoesNotExist:
            raise NotFound('there is no ROIs annotation step with label %s', label)

    def _find_by_rois_annotation_step(self, label):
        try:
            annotation_step = self._find_rois_annotation_step(label)
            return SlideQualityControl.objects.get(
                rois_annotation_step=annotation_step
            )
        except SlideQualityControl.DoesNotExist:
            raise NotFound('unable to find quality control data')

    def get(self, request, label, format=None):
        qc_obj = self._find_by_rois_annotation_step(label)
        serializer = SlideQualityControlSerializer(qc_obj)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    def post(self, request, label, format=None):
        rois_annotation_step = self._find_rois_annotation_step(label)
        qc_data = request.data
        qc_data['reviewer'] = request.user.username
        qc_data['slide'] = rois_annotation_step.slide.id
        qc_data['rois_annotation_step'] = rois_annotation_step.id

        logger.debug('Serializing data %r -- Object class %r', qc_data, SlideQualityControl)

        serializer = SlideQualityControlSerializer(data=qc_data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError:
                return Response({
                    'status': 'ERROR',
                    'message': 'duplicated entry for slide %s' % slide
                }, status=status.HTTP_409_CONFLICT)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, label, format=None):
        qc_obj = self._find_by_rois_annotation_step(label)
        try:
            qc_obj.delete()
        except IntegrityError:
            return Response({
                'status': 'ERROR',
                'message': 'unable to complete delete operation, there are still references to this object'
            }, status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)
