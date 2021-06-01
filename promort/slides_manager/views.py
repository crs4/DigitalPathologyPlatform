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

from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from django.db import IntegrityError

from view_templates.views import GenericDetailView, GenericListView

from slides_manager.models import Laboratory, Case, Slide, SlideEvaluation, SlidesSet, SlidesSetItem
from slides_manager.serializers import LaboratorySerializer, LaboratoryDetailSerializer, \
    CaseSerializer, CaseDetailedSerializer, SlideSerializer, SlideDetailSerializer, \
    SlideEvaluationSerializer, SlidesSetSerializer, SlidesSetDetailedSerializer, \
    SlidesSetItemSerializer, SlidesSetItemDetailedSerializer
from reviews_manager.models import ROIsAnnotationStep

import logging
logger = logging.getLogger('promort')


class LaboratoryList(GenericListView):
    model = Laboratory
    model_serializer = LaboratorySerializer
    permission_classes = (permissions.IsAuthenticated,)


class LaboratoryDetail(GenericDetailView):
    model = Laboratory
    model_serializer = LaboratoryDetailSerializer
    permission_classes = (permissions.IsAuthenticated,)


class LaboratoryCaseLink(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def _find_laboratory(self, label):
        try:
            return Laboratory.objects.get(label__iexact=label)
        except Laboratory.DoesNotExist:
            raise NotFound('There is no Laboratory with label %s' % label)

    def _find_case(self, id):
        try:
            return Case.objects.get(pk=id)
        except Case.DoesNotExist:
            raise NotFound('There is no case with ID %s' % id)

    def put(self, request, laboratory, case, format=None):
        lab_obj = self._find_laboratory(laboratory)
        case_obj = self._find_case(case)
        # laboratory is case insensitive now
        serializer = CaseSerializer(case_obj, data={'laboratory': lab_obj.label}, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


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


class SlideEvaluationDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def _find_rois_annotation_step(self, label):
        try:
            return ROIsAnnotationStep.objects.get(label=label)
        except ROIsAnnotationStep.DoesNotExist:
            raise NotFound('There is no ROIs annotation step with label %s', label)

    def _find_by_rois_annotation_step(self, label):
        try:
            annotation_step = self._find_rois_annotation_step(label)
            return SlideEvaluation.objects.get(
                rois_annotation_step=annotation_step
            )
        except SlideEvaluation.DoesNotExist:
            raise NotFound('Unable to find quality control data')

    def get(self, request, label, format=None):
        evaluation_obj = self._find_by_rois_annotation_step(label)
        serializer = SlideEvaluationSerializer(evaluation_obj)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    def post(self, request, label, format=None):
        rois_annotation_step = self._find_rois_annotation_step(label)
        evaluation_data = request.data
        evaluation_data['reviewer'] = request.user.username
        evaluation_data['slide'] = rois_annotation_step.slide.id
        evaluation_data['rois_annotation_step'] = rois_annotation_step.id

        logger.debug('Serializing data %r -- Object class %r', evaluation_data, SlideEvaluation)

        serializer = SlideEvaluationSerializer(data=evaluation_data)
        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError:
                return Response({
                    'status': 'ERROR',
                    'message': 'duplicated entry for slide %s' % rois_annotation_step.slide.id
                }, status=status.HTTP_409_CONFLICT)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, label, format=None):
        qc_obj = self._find_by_rois_annotation_step(label)
        try:
            qc_obj.delete()
        except IntegrityError:
            return Response({
                'status': 'ERROR',
                'message': 'unable to complete delete operation, there are still references to this object'
            }, status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SlidesSetList(GenericListView):
    model = SlidesSet
    model_serializer = SlidesSetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class SlidesSetDetail(GenericDetailView):
    model = SlidesSet
    model_serializer = SlidesSetDetailedSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
