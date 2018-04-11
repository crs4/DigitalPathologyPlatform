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

from reviews_manager.models import ROIsAnnotationStep
from reviews_manager.serializers import ROIsAnnotationStepFullSerializer, \
    ROIsAnnotationStepROIsTreeSerializer
from rois_manager.models import Slice, Core, FocusRegion
from rois_manager.serializers import SliceSerializer, SliceDetailsSerializer, \
    CoreSerializer, CoreDetailsSerializer, FocusRegionSerializer

import logging
logger = logging.getLogger('promort')


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
