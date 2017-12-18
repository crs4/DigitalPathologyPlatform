from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from odin.permissions import CanEnterGodMode

from slides_manager.models import SlideEvaluation

import logging
logger = logging.getLogger('promort')


class BadSlideDetails(APIView):
    permission_classes = (CanEnterGodMode,)

    def _load_bad_quality_controls(self):
        return SlideEvaluation.objects.filter(adequate_slide=False)

    def _get_not_adequacy_reason(self, coded_string):
        choices_map = dict((x[0], x[1]) for x in SlideEvaluation.NOT_ADEQUACY_REASONS_CHOICES)
        return choices_map[coded_string]

    def _get_laboratory(self, bad_quality_obj):
        if bad_quality_obj.slide.case.laboratory:
            return bad_quality_obj.slide.case.laboratory.label
        else:
            return None

    def _get_slides_infos(self, bad_quality_objs):
        return [{
            'slide_id': bq.slide.id,
            'laboratory': self._get_laboratory(bq),
            'reviewer': bq.reviewer.username,
            'review_id': bq.rois_annotation_step.label,
            'reason': self._get_not_adequacy_reason(bq.not_adequacy_reason),
            'notes': bq.notes
        } for bq in bad_quality_objs]

    def get(self, request, format=None):
        bad_qcs = self._load_bad_quality_controls()
        bad_qcs_infos = self._get_slides_infos(bad_qcs)
        return Response(bad_qcs_infos, status=status.HTTP_200_OK)
