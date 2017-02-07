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

    def _find_by_rois_annotation_step(self, case_id, username, slide_id):
        try:
            annotation = ROIsAnnotation.objects.get(
                case=case_id,
                reviewer=User.objects.get(username=username)
            )
            annotation_step = ROIsAnnotationStep.objects.get(
                rois_annotation=annotation,
                slide=slide_id
            )
            return SlideQualityControl.objects.get(
                rois_annotation_step=annotation_step
            )
        except ROIsAnnotation.DoesNotExist:
            raise NotFound('unable to find ROIs annotation for case %s assigned to user %s' % (case_id, username))
        except ROIsAnnotationStep.DoesNotExist:
            raise NotFound('unable to find ROIs annotation step for slide %s' % slide_id)
        except SlideQualityControl.DoesNotExist:
            raise NotFound('unable to find quality control data')

    def get(self, request, case, reviewer, slide, format=None):
        qc_obj = self._find_by_rois_annotation_step(case, reviewer, slide)
        serializer = SlideQualityControlSerializer(qc_obj)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    def post(self, request, case, reviewer, slide, format=None):
        qc_data = request.data
        qc_data['reviewer'] = reviewer
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

    def delete(self, request, case, reviewer, slide, format=None):
        qc_obj = self._find_by_rois_annotation_step(case, reviewer, slide)
        try:
            qc_obj.delete()
        except IntegrityError:
            return Response({
                'status': 'ERROR',
                'message': 'unable to complete delete operation, there are still references to this object'
            }, status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)
