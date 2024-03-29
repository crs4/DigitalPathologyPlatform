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
from collections import Counter

from rest_framework.views import APIView
from rest_framework import permissions, status, exceptions
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from django.db import IntegrityError

from view_templates.views import GenericDetailView
from rois_manager.models import Core
from rois_manager.serializers import CoreSerializer
from reviews_manager.models import ROIsAnnotationStep, ClinicalAnnotationStep
from reviews_manager.serializers import ClinicalAnnotationStepROIsTreeSerializer
from clinical_annotations_manager.models import SliceAnnotation, CoreAnnotation, FocusRegionAnnotation, GleasonPattern
from clinical_annotations_manager.serializers import SliceAnnotationSerializer, SliceAnnotationDetailsSerializer,\
    CoreAnnotationSerializer, CoreAnnotationDetailsSerializer, FocusRegionAnnotationSerializer, \
    FocusRegionAnnotationDetailsSerializer, GleasonPatternSerializer

import logging
logger = logging.getLogger('promort')


class AnnotatedROIsTreeList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def _get_clinical_annotation_step_id(self, clinical_annotation_step_label):
        try:
            obj = ClinicalAnnotationStep.objects.get(label=clinical_annotation_step_label)
            return obj.id
        except ClinicalAnnotationStep.DoesNotExist:
            raise NotFound('There is no Clinical Annotation step with label \'%s\'' % clinical_annotation_step_label)

    def _update_annotation(self, roi_data, clinical_annotation_step_id):
        annotation_status = {'annotated': False}
        annotations = roi_data.pop('clinical_annotations')
        for annotation in annotations:
            if annotation['annotation_step'] == int(clinical_annotation_step_id):
                annotation_status['annotated'] = True
        roi_data.update(annotation_status)
    
    def _prepare_gleason_patterns(self, gleason_patterns, clinical_annotation_step_id):
        filtered_gp = list()
        for gp in gleason_patterns:
            if gp['annotation_step'] == int(clinical_annotation_step_id):
                gp['annotated'] = True
                filtered_gp.append(gp)
        return filtered_gp

    def get(self, request, rois_annotation_step, clinical_annotation_step, format=None):
        try:
            obj = ROIsAnnotationStep.objects.get(label=rois_annotation_step)
        except ROIsAnnotationStep.DoesNotExist:
            raise NotFound('There is no ROIsAnnotationStep with ID %s' % rois_annotation_step)
        serializer = ClinicalAnnotationStepROIsTreeSerializer(obj)
        clinical_annotation_step_id = self._get_clinical_annotation_step_id(clinical_annotation_step)
        rois_tree = serializer.data
        for slice in rois_tree['slices']:
            self._update_annotation(slice, clinical_annotation_step_id)
            for core in slice['cores']:
                self._update_annotation(core, clinical_annotation_step_id)
                for focus_region in core['focus_regions']:
                    self._update_annotation(focus_region, clinical_annotation_step_id)
                    if len(focus_region['gleason_patterns']) > 0:
                        focus_region['gleason_patterns'] = self._prepare_gleason_patterns(
                            focus_region['gleason_patterns'], clinical_annotation_step_id
                        )
        return Response(rois_tree, status=status.HTTP_200_OK)


class ClinicalAnnotationStepAnnotationsList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, clinical_annotation_step):
        annotations = []
        slice_annotations = SliceAnnotation.objects.filter(annotation_step__label=clinical_annotation_step)
        annotations.extend(SliceAnnotationSerializer(slice_annotations, many=True).data)
        core_annotations = CoreAnnotation.objects.filter(annotation_step__label=clinical_annotation_step)
        annotations.extend(CoreAnnotationSerializer(core_annotations, many=True).data)
        focus_region_annotations = FocusRegionAnnotation.objects.filter(annotation_step__label=clinical_annotation_step)
        annotations.extend(FocusRegionAnnotationSerializer(focus_region_annotations, many=True).data)
        return Response(annotations, status=status.HTTP_200_OK)

    def delete(self, request, clinical_annotation_step):
        SliceAnnotation.objects.filter(annotation_step__label=clinical_annotation_step).delete()
        CoreAnnotation.objects.filter(annotation_step__label=clinical_annotation_step).delete()
        FocusRegionAnnotation.objects.filter(annotation_step__label=clinical_annotation_step).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SliceAnnotationList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, slice_id, format=None):
        slice_annotations = SliceAnnotation.objects.filter(slice=slice_id)
        serializer = SliceAnnotationSerializer(slice_annotations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClinicalAnnotationStepObject(APIView):
    def _get_clinical_annotation_step_id(self, clinical_annotation_step_label):
        try:
            obj = ClinicalAnnotationStep.objects.get(label=clinical_annotation_step_label)
            return obj.id
        except ClinicalAnnotationStep.DoesNotExist:
            raise NotFound('There is no Clinical Annotation step with label \'%s\'' % clinical_annotation_step_label)


class SliceAnnotationDetail(ClinicalAnnotationStepObject):
    permission_classes = (permissions.IsAuthenticated,)

    def _get_annotation(self, slice_id, annotation_step_label):
        annotation_step_id = self._get_clinical_annotation_step_id(annotation_step_label)
        try:
            return SliceAnnotation.objects.get(slice=slice_id, annotation_step=annotation_step_id)
        except SliceAnnotation.DoesNotExist:
            raise NotFound('There is no annotation for slice %r related to annotation step %r' %
                           (slice_id, annotation_step_label))

    def get(self, request, slice_id, label, format=None):
        slice_annotation = self._get_annotation(slice_id, label)
        serializer = SliceAnnotationDetailsSerializer(slice_annotation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, slice_id, label, format=None):
        slice_annotation_data = request.data
        slice_annotation_data['slice'] = slice_id
        slice_annotation_data['annotation_step'] = self._get_clinical_annotation_step_id(label)
        slice_annotation_data['author'] = request.user.username
        serializer = SliceAnnotationSerializer(data=slice_annotation_data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError:
                return Response({
                    'status': 'ERROR',
                    'message': 'duplicated annotation for slice %d of annotation step %s' %
                               (slice_id, label)
                }, status=status.HTTP_409_CONFLICT)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slice_id, label, format=None):
        slice_annotation = self._get_annotation(slice_id, label)
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


class CoreAnnotationDetail(ClinicalAnnotationStepObject):
    permission_classes = (permissions.IsAuthenticated,)

    def _get_annotation(self, core_id, annotation_step_label):
        annotation_step_id = self._get_clinical_annotation_step_id(annotation_step_label)
        try:
            return CoreAnnotation.objects.get(core=core_id, annotation_step=annotation_step_id)
        except CoreAnnotation.DoesNotExist:
            raise NotFound('There is no annotation for core %r related to annotation step %r' %
                           (core_id, annotation_step_id))

    def get(self, request, core_id, label, format=None):
        core_annotation = self._get_annotation(core_id, label)
        serializer = CoreAnnotationDetailsSerializer(core_annotation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, core_id, label, format=None):
        core_annotation_data = request.data
        core_annotation_data['core'] = core_id
        core_annotation_data['annotation_step'] = self._get_clinical_annotation_step_id(label)
        core_annotation_data['author'] = request.user.username
        serializer = CoreAnnotationSerializer(data=core_annotation_data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError:
                return Response({
                    'status': 'ERROR',
                    'message': 'duplicated annotation for core %d of annotation step %s' %
                               (core_id, label)
                }, status=status.HTTP_409_CONFLICT)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, core_id, label, format=None):
        core_annotation = self._get_annotation(core_id, label)
        try:
            core_annotation.delete()
        except IntegrityError:
            return Response({
                'status': 'ERROR',
                'message': 'unable to complete delete operation, there are still references to this object'
            }, status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CoreGleasonDetail(APIView):
    permissions = (permissions.IsAuthenticated,)

    def _get_gleason_elements(self, core_obj, annotation_step_label):
        gleason_elements = list()
        for fr in core_obj.focus_regions.all():
            gleason_elements.extend(
                GleasonPattern.objects.filter(
                    focus_region=fr,
                    annotation_step__label=annotation_step_label
                ).all()
            )
        return gleason_elements

    def _get_gleason_coverage(self, gleason_patterns_area):
        total_area = sum(gleason_patterns_area.values())
        gleason_coverage = dict()
        for gp, gpa in gleason_patterns_area.items():
            gleason_coverage[gp] = (100 * gpa/total_area)
        return gleason_coverage
    
    def _get_primary_and_secondary_gleason(self, gleason_coverage):
        if len(gleason_coverage) == 0:
            return None, None
        primary_gleason = max(gleason_coverage, key=gleason_coverage.get)
        gleason_coverage.pop(primary_gleason)
        if len(gleason_coverage) == 0:
            secondary_gleason = primary_gleason
        else:
            secondary_gleason = max(gleason_coverage)
        return primary_gleason, secondary_gleason 
            
    def _get_gleason_details(self, core_obj, annotation_step_label):
        gleason_elements = self._get_gleason_elements(core_obj, annotation_step_label)
        gleason_total_area = Counter()
        gleason_shapes = dict()
        gleason_subregions = dict()
        for ge in gleason_elements:
            gleason_total_area[ge.gleason_type] += ge.area
            gleason_shapes.setdefault(ge.gleason_type, []).append(ge.label)
            gleason_subregions.setdefault(ge.gleason_type, set())
            for subr in ge.subregions.all():
                gleason_subregions[ge.gleason_type].add(json.loads(subr.details_json)["type"])
        gleason_coverage = self._get_gleason_coverage(gleason_total_area)
        gleason_details = {"details": {}}
        for gtype in gleason_shapes.keys():
            gleason_details["details"][gtype] = {
                "shapes": gleason_shapes[gtype],
                "total_area": gleason_total_area[gtype],
                "total_coverage": round(gleason_coverage[gtype], 2),
                "subregions": gleason_subregions[gtype]
            }
        primary_gleason, secondary_gleason = self._get_primary_and_secondary_gleason(gleason_coverage)
        gleason_details.update({
            "primary_gleason": primary_gleason,
            "secondary_gleason": secondary_gleason
        })
        return gleason_details

    def get(self, request, core_id, label, format=None):
        try:
            core = Core.objects.get(pk__iexact=core_id)
        except Core.DoesNotExist:
            raise NotFound('There is no Core with ID {0}'.format(core_id))
        gleason_details = self._get_gleason_details(core, label)
        core_data = CoreSerializer(core).data
        core_data.update(gleason_details)
        core_data.pop("roi_json")
        return Response(core_data, status=status.HTTP_200_OK)


class FocusRegionAnnotationList(APIView):
    permissions = (permissions.IsAuthenticated,)

    def get(self, request, focus_region_id, format=None):
        focus_region_annotations = FocusRegionAnnotation.objects.filter(focus_region=focus_region_id)
        serializer = FocusRegionAnnotationSerializer(focus_region_annotations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FocusRegionAnnotationDetail(ClinicalAnnotationStepObject):
    permission_classes = (permissions.IsAuthenticated,)

    def _get_annotation(self, focus_region_id, annotation_step_label):
        annotation_step_id = self._get_clinical_annotation_step_id(annotation_step_label)
        try:
            return FocusRegionAnnotation.objects.get(focus_region=focus_region_id,
                                                     annotation_step=annotation_step_id)
        except FocusRegionAnnotation.DoesNotExist:
            raise NotFound('There is no annotation for focus_region %r related to annotation step %r' %
                           (focus_region_id, annotation_step_id))

    def get(self, request, focus_region_id, label, format=None):
        focus_region_annotation = self._get_annotation(focus_region_id, label)
        serializer = FocusRegionAnnotationDetailsSerializer(focus_region_annotation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, focus_region_id, label, format=None):
        focus_region_annotation_data = request.data
        focus_region_annotation_data['focus_region'] = focus_region_id
        focus_region_annotation_data['annotation_step'] = self._get_clinical_annotation_step_id(label)
        focus_region_annotation_data['author'] = request.user.username
        if focus_region_annotation_data.get('cellular_density_helper_json'):
            focus_region_annotation_data['cellular_density_helper_json'] = \
                json.dumps(focus_region_annotation_data['cellular_density_helper_json'])
        serializer = FocusRegionAnnotationSerializer(data=focus_region_annotation_data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError:
                return Response({
                    'status': 'ERROR',
                    'message': 'duplicated annotation for focus region %d of annotation step %d' %
                               (focus_region_id, label)
                }, status=status.HTTP_409_CONFLICT)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, focus_region_id, label, format=None):
        focus_region_annotation = self._get_annotation(focus_region_id, label)
        try:
            focus_region_annotation.delete()
        except IntegrityError:
            return Response({
                'status': 'ERROR',
                'message': 'unable to complete delete operation, there are still references to this object'
            }, status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GleasonPatternList(ClinicalAnnotationStepObject):
    permissions = (permissions.IsAuthenticated,)

    def get(self, request, focus_region_id, label, format=None):
        gleason_patterns = GleasonPattern.objects.filter(
            focus_region=focus_region_id, annotation_step__label=label
        )
        serializer = GleasonPatternSerializer(gleason_patterns, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, focus_region_id, label, format=None):
        gleason_pattern_data = request.data
        gleason_pattern_data['focus_region'] = focus_region_id
        gleason_pattern_data['annotation_step'] = self._get_clinical_annotation_step_id(label)
        gleason_pattern_data['author'] = request.user.username
        serializer = GleasonPatternSerializer(data=gleason_pattern_data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError:
                return Response({
                    'status': 'ERROR',
                    'message': 'duplicated gleason pattern label {0} for annotation step {1}'.format(
                        gleason_pattern_data['label'], label
                    )
                }, status=status.HTTP_409_CONFLICT)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GleasonPatternDetail(GenericDetailView):
    model = GleasonPattern
    model_serializer = GleasonPatternSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def put(self, request, pk, format=None):
        raise exceptions.MethodNotAllowed(method='put')
