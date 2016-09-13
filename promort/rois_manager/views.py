try:
    import simplejson as json
except ImportError:
    import json

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import MethodNotAllowed

from django.db import IntegrityError

from view_templates.views import GenericDetailView

from slides_manager.models import Slide
from rois_manager.models import Slice, Core, CellularFocus
from rois_manager.serializers import SlideDetailsSerializer, SliceSerializer, \
    SliceDetailsSerializer, CoreSerializer, CoreDetailsSerializer, CellularFocusSerializer

import logging
logger = logging.getLogger('promort')


class SliceList(GenericDetailView):
    model = Slide
    model_serializer = SlideDetailsSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request, pk, format=None):
        raise MethodNotAllowed('DELETE')

    def post(self, request, pk, format=None):
        slice_data = request.data
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


class CoreList(GenericDetailView):
    model = Slice
    model_serializer = SliceDetailsSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request, pk, format=None):
        raise MethodNotAllowed('DELETE')

    def post(self, request, pk, format=None):
        core_data = request.data
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


class CellularFocusList(GenericDetailView):
    model = Core
    model_serializer = CoreDetailsSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request, pk, format=None):
        raise MethodNotAllowed('DELETE')

    def post(self, request, pk, format=None):
        cellular_focus_data = request.data
        cellular_focus_data['core'] = pk

        logger.debug('Serializing data %r -- Object class %r', cellular_focus_data, CellularFocus)

        serializer = CellularFocusSerializer(data=cellular_focus_data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError:
                return Response({
                    'status': 'ERROR',
                    'message': 'duplicated cellular focus label %s for core %s' %
                               (cellular_focus_data['label'], pk)
                }, status=status.HTTP_409_CONFLICT)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class CellularFocusDetail(GenericDetailView):
    model = CellularFocus
    model_serializer = CellularFocusSerializer
    permission_classes = (permissions.IsAuthenticated,)
