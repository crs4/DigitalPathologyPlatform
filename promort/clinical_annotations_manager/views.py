try:
    import simplejson as json
except ImportError:
    import json

from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from django.db import IntegrityError

from reviews_manager.models import ROIsAnnotationStep
from reviews_manager.serializers import ClinicalAnnotationStepROIsTreeSerializer
from clinical_annotations_manager.models import SliceAnnotation, CoreAnnotation, FocusRegionAnnotation
from clinical_annotations_manager.serializers import SliceAnnotationSerializer, SliceAnnotationDetailsSerializer,\
    CoreAnnotationSerializer, CoreAnnotationDetailsSerializer, FocusRegionAnnotationSerializer, \
    FocusRegionAnnotationDetailsSerializer

import logging
logger = logging.getLogger('promort')


class AnnotatedROIsTreeList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def _update_annotation(self, roi_data, clinical_annotation_step):
        annotation_status = {'annotated': False}
        annotations = roi_data.pop('clinical_annotations')
        for annotation in annotations:
            if annotation['annotation_step'] == int(clinical_annotation_step):
                annotation_status['annotated'] = True
        roi_data.update(annotation_status)

    def get(self, request, rois_annotation_step, clinical_annotation_step, format=None):
        try:
            obj = ROIsAnnotationStep.objects.get(pk=rois_annotation_step)
        except ROIsAnnotationStep.DoesNotExist:
            raise NotFound('There is no ROIsAnnotationStep with ID %s' % rois_annotation_step)
        serializer = ClinicalAnnotationStepROIsTreeSerializer(obj)
        rois_tree = serializer.data
        for slice in rois_tree['slices']:
            self._update_annotation(slice, clinical_annotation_step)
            for core in slice['cores']:
                self._update_annotation(core, clinical_annotation_step)
                for focus_region in core['focus_regions']:
                    self._update_annotation(focus_region, clinical_annotation_step)
        return Response(rois_tree, status=status.HTTP_200_OK)


class SliceAnnotationList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, slice_id, format=None):
        slice_annotations = SliceAnnotation.objects.filter(slice=slice_id)
        serializer = SliceAnnotationSerializer(slice_annotations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SliceAnnotationDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def _get_annotation(self, slice_id, annotation_step_id):
        try:
            return SliceAnnotation.objects.get(slice=slice_id, annotation_step=annotation_step_id)
        except SliceAnnotation.DoesNotExist:
            raise NotFound('There is no annotation for slice %d related to annotation step %d' %
                           (slice_id, annotation_step_id))

    def get(self, request, slice_id, annotation_step_id, format=None):
        slice_annotation = self._get_annotation(slice_id, annotation_step_id)
        serializer = SliceAnnotationDetailsSerializer(slice_annotation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, slice_id, annotation_step_id, format=None):
        slice_annotation_data = request.data
        slice_annotation_data['slice'] = slice_id
        slice_annotation_data['annotation_step'] = annotation_step_id
        slice_annotation_data['author'] = request.user.username
        serializer = SliceAnnotationSerializer(data=slice_annotation_data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError:
                return Response({
                    'status': 'ERROR',
                    'message': 'duplicated annotation for slice %d of annotation step %d' %
                               (slice_id, annotation_step_id)
                }, status=status.HTTP_409_CONFLICT)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slice_id, annotation_step_id, format=None):
        slice_annotation = self._get_annotation(slice_id, annotation_step_id)
        try:
            slice_annotation.delete()
        except IntegrityError:
            return Response({
                'status': 'ERROR',
                'message': 'unable to complete delete operation, there are still references to this object'
            }, status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CoreAnnotationList(APIView):
    permissions = (permissions.IsAuthenticated,)

    def get(self, request, core_id, format=None):
        core_annotations = CoreAnnotation.objects.filter(core=core_id)
        serializer = CoreAnnotationSerializer(core_annotations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CoreAnnotationDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def _get_annotation(self, core_id, annotation_step_id):
        try:
            return CoreAnnotation.objects.get(core=core_id, annotation_step=annotation_step_id)
        except CoreAnnotation.DoesNotExist:
            raise NotFound('There is no annotation for core %d related to annotation step %d' %
                           (core_id, annotation_step_id))

    def get(self, request, core_id, annotation_step_id, format=None):
        core_annotation = self._get_annotation(core_id, annotation_step_id)
        serializer = CoreAnnotationDetailsSerializer(core_annotation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, core_id, annotation_step_id, format=None):
        core_annotation_data = request.data
        core_annotation_data['core'] = core_id
        core_annotation_data['annotation_step'] = annotation_step_id
        core_annotation_data['author'] = request.user.username
        serializer = CoreAnnotationSerializer(data=core_annotation_data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError:
                return Response({
                    'status': 'ERROR',
                    'message': 'duplicated annotation for core %d of annotation step %d' %
                               (core_id, annotation_step_id)
                }, status=status.HTTP_409_CONFLICT)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, core_id, annotation_step_id, format=None):
        core_annotation = self._get_annotation(core_id, annotation_step_id)
        try:
            core_annotation.delete()
        except IntegrityError:
            return Response({
                'status': 'ERROR',
                'message': 'unable to complete delete operation, there are still references to this object'
            }, status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FocusRegionAnnotationList(APIView):
    permissions = (permissions.IsAuthenticated,)

    def get(self, request, focus_region_id, format=None):
        focus_region_annotations = FocusRegionAnnotation.objects.filter(focus_region=focus_region_id)
        serializer = FocusRegionAnnotationSerializer(focus_region_annotations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FocusRegionAnnotationDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def _get_annotation(self, focus_region_id, annotation_step_id):
        try:
            return FocusRegionAnnotation.objects.get(focus_region=focus_region_id,
                                                     annotation_step=annotation_step_id)
        except FocusRegionAnnotation.DoesNotExist:
            raise NotFound('There is no annotation for focus_region %d related to annotation step %d' %
                           (focus_region_id, annotation_step_id))

    def get(self, request, focus_region_id, annotation_step_id, format=None):
        focus_region_annotation = self._get_annotation(focus_region_id, annotation_step_id)
        serializer = FocusRegionAnnotationDetailsSerializer(focus_region_annotation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, focus_region_id, annotation_step_id, format=None):
        focus_region_annotation_data = request.data
        focus_region_annotation_data['focus_region'] = focus_region_id
        focus_region_annotation_data['annotation_step'] = annotation_step_id
        focus_region_annotation_data['author'] = request.user.username
        serializer = CoreAnnotationSerializer(data=focus_region_annotation_data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError:
                return Response({
                    'status': 'ERROR',
                    'message': 'duplicated annotation for focus region %d of annotation step %d' %
                               (focus_region_id, annotation_step_id)
                }, status=status.HTTP_409_CONFLICT)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, focus_region_id, annotation_step_id, format=None):
        focus_region_annotation = self._get_annotation(focus_region_id, annotation_step_id)
        try:
            focus_region_annotation.delete()
        except IntegrityError:
            return Response({
                'status': 'ERROR',
                'message': 'unable to complete delete operation, there are still references to this object'
            }, status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)
