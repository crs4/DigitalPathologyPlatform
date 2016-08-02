from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from django.db import IntegrityError

from view_templates.views import GenericDetailView, GenericListView

from slides_manager.models import Case, Slide, SlideQualityControl
from slides_manager.serializers import CaseSerializer, CaseDetailedSerializer,\
    SlideSerializer, SlideDetailSerializer, SlideQualityControlSerializer

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

    def _find_by_slide(self, slide_id):
        try:
            return SlideQualityControl.objects.get(slide=slide_id)
        except SlideQualityControl.DoesNotExist:
            raise NotFound('Unable to find quality control data for slide ID \'%s\'' % slide_id)

    def get(self, request, slide, format=None):
        qc_obj = self._find_by_slide(slide)
        serializer = SlideQualityControlSerializer(qc_obj)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    def post(self, request, slide, format=None):
        qc_data = request.data
        qc_data['reviewer'] = request.user.username
        qc_data['slide'] = slide

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

    def delete(self, request, slide, format=None):
        qc_obj = self._find_by_slide(slide)
        try:
            qc_obj.delete()
        except IntegrityError:
            return Response({
                'status': 'ERROR',
                'message': 'unable to complete delete operation, there are still references to this object'
            }, status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)
