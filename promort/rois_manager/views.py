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

from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from django.db import IntegrityError

from view_templates.views import GenericReadOnlyDetailView, GenericDetailView

from slides_manager.models import Slide
from reviews_manager.models import ROIsAnnotationStep
from reviews_manager.serializers import ROIsAnnotationStepFullSerializer, \
    ROIsAnnotationStepROIsTreeSerializer
from rois_manager.models import Slice, Core, FocusRegion
from rois_manager.serializers import SliceSerializer, SliceDetailsSerializer, \
    CoreSerializer, CoreDetailsSerializer, FocusRegionSerializer

import logging
logger = logging.getLogger('promort')


class SlideROIsList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def _serialize_rois_data(self, rois, roi_type, annotation_step):
        rois_data = []
        roi_parent_type = {
            'slice': None,
            'core': 'slice',
            'focus_region': 'core'
        }
        for r in rois:
            roi_details = {
                'roi_id': r.id,
                'roi_type': roi_type,
                'annotation_step': annotation_step,
                'parent_type': roi_parent_type[roi_type],
                'parent_id': None
            }
            if roi_type == 'core':
                roi_details['parent_id'] = r.slice.id
            elif roi_type == 'focus_region':
                roi_details['parent_id'] = r.core.id
            rois_data.append(roi_details)
        return rois_data

    def get(self, request, pk, format=None):
        try:
            slide_obj = Slide.objects.get(id=pk)
        except Slide.DoesNotExist:
            raise NotFound('There is no Slide with label {0}'.format(pk))
        roi_type = request.query_params.get('roi_type')
        rois_annotation_steps = ROIsAnnotationStep.objects.filter(slide=slide_obj, completion_date__isnull=False)
        rois = []
        if roi_type is None:
            for step in rois_annotation_steps:
                rois.extend(self._serialize_rois_data(step.slices.all(), 'slice', step.label))
                rois.extend(self._serialize_rois_data(step.cores, 'core', step.label))
                rois.extend(self._serialize_rois_data(step.focus_regions, 'focus_region', step.label))
        else:
            if roi_type == 'slice':
                for step in rois_annotation_steps:
                    print(step.label)
                    rois.extend(self._serialize_rois_data(step.slices.all(), 'slice', step.label))
            elif roi_type == 'core':
                for step in rois_annotation_steps:
                    rois.extend(self._serialize_rois_data(step.cores, 'core', step.label))
            elif roi_type == 'focus_region':
                for step in rois_annotation_steps:
                    rois.extend(self._serialize_rois_data(step.focus_regions, 'focus_region', step.label))
            else:
                return Response(
                    '{0} is not a valid ROI type'.format(roi_type), 
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(rois, status=status.HTTP_200_OK)


class ROIsTreeList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, label, format=None):
        try:
            obj = ROIsAnnotationStep.objects.get(label=label)
        except ROIsAnnotationStep.DoesNotExist:
            raise NotFound('There is no ROIsAnnotationStep with label %s' % label)
        serializer = ROIsAnnotationStepROIsTreeSerializer(obj)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    def delete(self, request, label, format=None):
        slices = Slice.objects.filter(annotation_step__label=label)
        for s in slices:
            s.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SliceList(APIView):
    model = ROIsAnnotationStep
    model_serializer = ROIsAnnotationStepFullSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def _find_rois_annotation_step(self, label):
        try:
            return ROIsAnnotationStep.objects.get(label=label)
        except ROIsAnnotationStep.DoesNotExist:
            raise NotFound('There is no ROIsAnnotationStep with label %s' % label)

    def get(self, request, label, format=None):
        annotation_step = self._find_rois_annotation_step(label)
        serializer = self.model_serializer(annotation_step)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, label, format=None):
        annotation_step = self._find_rois_annotation_step(label)
        slice_data = request.data
        slice_data['annotation_step'] = annotation_step.id
        slice_data['author'] = request.user.username

        serializer = SliceSerializer(data=slice_data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError:
                return Response({
                    'status': 'ERROR',
                    'message': 'duplicated slice label %s' % (slice_data['label'])
                }, status=status.HTTP_409_CONFLICT)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class SliceDetail(GenericDetailView):
    model = Slice
    model_serializer = SliceSerializer
    permission_classes = (permissions.IsAuthenticated,)


class CoreList(GenericReadOnlyDetailView):
    model = Slice
    model_serializer = SliceDetailsSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk, format=None):
        core_data = request.data
        core_data['author'] = request.user.username
        core_data['slice'] = pk

        serializer = CoreSerializer(data=core_data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError:
                return Response({
                    'status': 'ERROR',
                    'message': 'duplicated core label %s for slice %s' % (core_data['label'], pk)
                }, status=status.HTTP_409_CONFLICT)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class CoreDetail(GenericDetailView):
    model = Core
    model_serializer = CoreSerializer
    permission_classes = (permissions.IsAuthenticated,)


class FocusRegionList(GenericReadOnlyDetailView):
    model = Core
    model_serializer = CoreDetailsSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk, format=None):
        focus_region_data = request.data
        focus_region_data['author'] = request.user.username
        focus_region_data['core'] = pk

        serializer = FocusRegionSerializer(data=focus_region_data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError:
                return Response({
                    'status': 'ERROR',
                    'message': 'duplicated focus region label %s for core %s' %
                               (focus_region_data['label'], pk)
                }, status=status.HTTP_409_CONFLICT)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class FocusRegionDetail(GenericDetailView):
    model = FocusRegion
    model_serializer = FocusRegionSerializer
    permission_classes = (permissions.IsAuthenticated,)
