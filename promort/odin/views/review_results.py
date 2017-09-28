from collections import Counter
import operator

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from odin.permissions import CanEnterGodMode

from slides_manager.models import Case, Slide
from reviews_manager.models import ClinicalAnnotation, ReviewsComparison

import logging
logger = logging.getLogger('promort')


class CaseReviewResults(APIView):
    permission_classes = (CanEnterGodMode,)

    def _get_case(self, case):
        try:
            return Case.objects.get(id=case)
        except Case.DoesNotExist:
            raise NotFound('There is no Case with label %s' % case)

    # group ReviewComparison objects by ROIsAnnotation
    def _get_final_reviews_map(self, case):
        review_comparisons = ReviewsComparison.objects.filter(
            review_1__slide__in=(
                Slide.objects.filter(case=case)
            )
        )
        # filter, keep only review comparisons linked to completed reviews
        review_comparisons = [
            rc for rc in review_comparisons if
            (
                rc.linked_reviews_completed() and
                not rc.is_evaluation_pending()
                and rc.positive_quality_control
            )
        ]
        rc_map = dict()
        for rc in review_comparisons:
            rc_map.setdefault(rc.review_1.rois_review_step.rois_annotation, []).append(
                rc.review_3 if rc.review_3 else rc.review_1
            )
        return rc_map

    def _get_max(self, primary_scores_counter):
        ct2 = dict()
        for gleason, count in primary_scores_counter.iteritems():
            ct2.setdefault(count, []).append(gleason)
        return max(ct2[max(ct2.keys())])

    def _get_overall_score(self, clinical_annotation_steps):
        primary_gleason_scores = Counter()
        secondary_gleason_scores = set()
        for clinical_annotation_step in clinical_annotation_steps:
            core_annotations = clinical_annotation_step.core_annotations.all()
            if len(core_annotations) == 0:
                return dict()
            for c_ann in core_annotations:
                primary_gleason_scores[c_ann.primary_gleason] += 1
                secondary_gleason_scores.add(c_ann.secondary_gleason)
        return {
            'primary_score': self._get_max(primary_gleason_scores),
            'secondary_score': max(secondary_gleason_scores)
        }

    def _get_scores(self, reviews_map):
        return dict(
            (r_ann_obj.label, self._get_overall_score(c_ann_objs))
            for (r_ann_obj, c_ann_objs) in reviews_map.iteritems()
        )

    def get(self, request, case, format=None):
        case_obj = self._get_case(case)
        reviews_map = self._get_final_reviews_map(case_obj)
        if len(reviews_map) == 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        scores = self._get_scores(reviews_map)
        return Response(scores, status=status.HTTP_200_OK)



# class CaseReviewResultsDetails(CaseReviewResults):
#     pass
