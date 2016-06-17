from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from django.db import IntegrityError

from view_templates.views import GenericDetailView, GenericListView

from slides_manager.models import Case, Slide, SlideQualityControl
from slides_manager.serializers import CaseSerializer, CaseDetailedSerializer,\
    SlideSerializer, SlideDetailSerializer, SlideQualityControlSerializer


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


class SlideQualityControlList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk, format=None):
        qc_data = request.data
        qc_data['reviewer'] = request.user.username
        qc_data['slide'] = pk

        serializer = SlideQualityControlSerializer(data=qc_data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError:
                return Response({
                    'status': 'ERROR',
                    'message': 'duplicated entry for slide %s' % pk
                }, status=status.HTTP_409_CONFLICT)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)
