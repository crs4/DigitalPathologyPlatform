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

from django.core.mail import send_mail

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

import promort.settings as prs
from slides_manager.models import SlideEvaluation
from clinical_annotations_manager.models import ClinicalAnnotationStep, GleasonPattern

import logging
logger = logging.getLogger('promort')


@api_view()
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def get_ome_seadragon_base_url(request):
    return Response({
        'base_url': prs.OME_SEADRAGON_BASE_URL,
        'static_files_url': prs.OME_SEADRAGON_STATIC_FILES_URL
    }, status=status.HTTP_200_OK)


@api_view()
@permission_classes([permissions.IsAuthenticated])
def get_slide_stainings(request):
    staining_map = [
        {
            'value': st[0],
            'text': st[1]
        } for st in SlideEvaluation.STAINING_CHOICES
    ]
    return Response(staining_map, status=status.HTTP_200_OK)


@api_view()
@permission_classes([permissions.IsAuthenticated])
def get_slide_qc_not_adequacy_reasons(request):
    not_adequacy_reasons_map = [
        {
            'value': ch[0],
            'text': ch[1]
        } for ch in SlideEvaluation.NOT_ADEQUACY_REASONS_CHOICES
    ]
    return Response(not_adequacy_reasons_map, status=status.HTTP_200_OK)


@api_view()
@permission_classes([permissions.IsAuthenticated])
def get_clinical_step_rejection_reasons(request):
    rejection_reasons_map = [
        {
            'value': ch[0],
            'text': ch[1],
        } for ch in ClinicalAnnotationStep.REJECTION_REASONS_CHOICES
    ]
    return Response(rejection_reasons_map, status=status.HTTP_200_OK)


@api_view()
@permission_classes([permissions.IsAuthenticated])
def get_gleason_element_types(request):
    gleason_types_map = [
        {
            'value': ch[0],
            'text': ch[1]
        } for ch in GleasonPattern.GLEASON_TYPES
    ]
    return Response(gleason_types_map, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_user_report(request):
    message = """
------------------
USER: %s
------------------
PAGE: %s
------------------
BROWSER: %s
------------------
MESSAGE: %s
------------------
""" % (request.user.username, request.data.get('page_url'),
       request.data.get('browser'), request.data.get('message'))

    send_mail(
        subject=''.join([prs.REPORT_SUBJECT_PREFIX, request.data.get('subject')]),
        message=message,
        from_email=prs.EMAIL_HOST_USER,
        recipient_list=prs.REPORT_RECIPIENTS
    )
    return Response(status=status.HTTP_204_NO_CONTENT)
