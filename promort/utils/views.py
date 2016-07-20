from django.core.mail import send_mail

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

import promort.settings as prs
from slides_manager.models import SlideQualityControl

import logging
logger = logging.getLogger('promort')


@api_view()
@permission_classes([permissions.IsAuthenticated])
def get_ome_seadragon_base_url(request):
    return Response({
        'base_url': prs.OME_SEADRAGON_BASE_URL,
        'static_files_url': prs.OME_SEADRAGON_STATIC_FILES_URL
    }, status=status.HTTP_200_OK)


@api_view()
@permission_classes([permissions.IsAuthenticated])
def get_slide_qc_not_adequacy_reasons(request):
    not_adequacy_reasons_map = [
        {
            'value': ch[0],
            'text': ch[1]
        } for ch in SlideQualityControl.NOT_ADEQUACY_REASONS_CHOICES
    ]
    return Response(not_adequacy_reasons_map, status=status.HTTP_200_OK)


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
