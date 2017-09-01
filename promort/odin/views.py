from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from odin.permissions import CanEnterGodMode

from slides_manager.models import Slide, Case
from rois_manager.models import Slice, Core, FocusRegion
from rois_manager.serializers import SliceSerializer, CoreSerializer, FocusRegionSerializer
from reviews_manager.models import ClinicalAnnotation, ClinicalAnnotationStep,\
    ROIsAnnotation, ROIsAnnotationStep

import logging
logger = logging.getLogger('promort')


class CheckAccessPrivileges(APIView):
    permission_classes = (CanEnterGodMode,)

    def get(self, request, format=None):
        return Response(status=status.HTTP_204_NO_CONTENT)


class GetOmeroID(APIView):
    permission_classes = (CanEnterGodMode,)

    def get(self, request, slide, format=None):
        try:
            slide = Slide.objects.get(id=slide)
            if slide.omero_id:
                return Response({
                    'omero_id': slide.omero_id
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'omero_id': None,
                    'message': 'Slide is not linked to an OMERO image'
                }, status=status.HTTP_200_OK)
        except Slide.DoesNotExist:
            raise NotFound('There is no slide with label %s' % slide)


class GetROIDetails(APIView):
    permission_classes = (CanEnterGodMode,)

    def _get_rois_annotation(self, case, reviewer):
        try:
            return ROIsAnnotation.objects.get(case__id=case,
                                              reviewer__username=reviewer)
        except ROIsAnnotation.DoesNotExist:
            raise NotFound('There is no ROIs Annotation for case %s assigned to reviewers %s' %
                           (case, reviewer))

    def _get_rois_annotation_step(self, rois_annotation_obj, slide):
        try:
            return ROIsAnnotationStep.objects.get(rois_annotation=rois_annotation_obj,
                                                  slide__id=slide)
        except ROIsAnnotationStep.DoesNotExist:
            raise NotFound('There is no ROIs Annotation Step associated to slide %s' % slide)

    def _get_slice(self, rois_annotation_step_obj, slice_label):
        try:
            return Slice.objects.get(label=slice_label, annotation_step=rois_annotation_step_obj)
        except Slice.DoesNotExist:
            raise NotFound('There is no slice with label %s' % slice_label)

    def _get_slices_ids(self, rois_annotation_step_obj):
        return rois_annotation_step_obj.slices.values_list('id', flat=True)

    def _get_core(self, slice_ids, core_label):
        try:
            return Core.objects.get(label=core_label, slice__id__in=slice_ids)
        except Core.DoesNotExist:
            raise NotFound('There is no core with label %s' % core_label)

    def _get_cores_ids(self, slices_ids):
        return Core.objects.filter(slice__id__in=slices_ids).values_list('id', flat=True)

    def _get_focus_region(self, cores_ids, focus_region_label):
        try:
            return FocusRegion.objects.get(label=focus_region_label,
                                           core__id__in=cores_ids)
        except FocusRegion.DoesNotExist:
            raise NotFound('There is no focus region with label %s' % focus_region_label)

    def _get_roi(self, rois_annotation_step_obj, roi_type, roi_label):
        if roi_type == 'slice':
            return self._get_slice(rois_annotation_step_obj, roi_label)
        elif roi_type == 'core':
            slice_ids = self._get_slices_ids(rois_annotation_step_obj)
            return self._get_core(slice_ids, roi_label)
        elif roi_type == 'focus_region':
            cores_ids = self._get_cores_ids(self._get_slices_ids(rois_annotation_step_obj))
            return self._get_focus_region(cores_ids, roi_label)
        else:
            # raise error
            pass

    def get(self, request, case, slide, reviewer, roi_type, roi_label, format=None):
        rois_annotation_obj = self._get_rois_annotation(case, reviewer)
        annotation_step_obj = self._get_rois_annotation_step(rois_annotation_obj, slide)
        roi_obj = self._get_roi(annotation_step_obj, roi_type, roi_label)
        serializers_map = {
            'slice': SliceSerializer,
            'core': CoreSerializer,
            'focus_region': FocusRegionSerializer
        }
        serializer = serializers_map[roi_type](roi_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)
