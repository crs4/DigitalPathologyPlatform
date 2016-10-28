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
from rois_manager.models import Slice, Core, FocusRegion
from rois_manager.serializers import SlideDetailsSerializer, SliceSerializer, \
    SliceDetailsSerializer, CoreSerializer, CoreDetailsSerializer, FocusRegionSerializer,\
    SlideROIsTreeSerializer

import logging
logger = logging.getLogger('promort')


class ROIsTreeList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk, format=None):
        try:
            logger.info('Searching for slide with ID %s' % pk)
            obj = Slide.objects.get(pk=pk)
        except Slide.DoesNotExist:
            raise NotFound('There is no Slide with ID %s' % pk)
        serializer = SlideROIsTreeSerializer(obj)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    def delete(self, request, pk, format=None):
        slices = Slice.objects.filter(slide=pk)
        for s in slices:
            s.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SliceList(GenericReadOnlyDetailView):
    model = Slide
    model_serializer = SlideDetailsSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk, format=None):
        slice_data = request.data
        slice_data['author'] = request.user.username
        slice_data['slide'] = pk

        logger.debug('Serializing data %r -- Object class %r', slice_data, Slice)

        serializer = SliceSerializer(data=slice_data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError:
                return Response({
                    'status': 'ERROR',
                    'message': 'duplicated slice label %s for slide %s' % (slice_data['label'], pk)
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

        logger.debug('Serializing data %r -- Object class %r', core_data, Core)

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

        logger.debug('Serializing data %r -- Object class %r', focus_region_data, FocusRegion)

        serializer = FocusRegionSerializer(data=focus_region_data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError, ie:
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
