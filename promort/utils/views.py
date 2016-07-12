from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

import promort.settings as prs

import logging
logger = logging.getLogger('promort')


@api_view()
@permission_classes([permissions.IsAuthenticated])
def get_ome_seadragon_base_url(request):
    return Response({
        'base_url': prs.OME_SEADRAGON_BASE_URL,
        'static_files_url': prs.OME_SEADRAGON_STATIC_FILES_URL
    }, status=status.HTTP_200_OK)
