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
@permission_classes(permissions.IsAuthenticated)
def get_slide_qc_not_adequacy_reasons(request):
    return [
        {
            'value': ch[0],
            'text': ch[1]
        } for ch in SlideQualityControl.NOT_ADEQUACY_REASONS_CHOICES
    ]
