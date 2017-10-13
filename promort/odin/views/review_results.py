from collections import Counter

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from odin.permissions import CanEnterGodMode

from slides_manager.models import Case
from reviews_manager.models import ReviewsComparison

import logging
logger = logging.getLogger('promort')


class CaseReviewResults(APIView):
    permission_classes = (CanEnterGodMode,)

    def _get_case(self, case):
        try:
            return Case.objects.get(id=case)
        except Case.DoesNotExist:
            raise NotFound('There is no Case with label %s' % case)

    def _filter_not_compared(self, review_comparisons_map):
        to_be_removed = []
        for r_ann, comparisons in review_comparisons_map.iteritems():
            for comp in comparisons:
                if comp.is_evaluation_pending() or \
                        (not comp.positive_match and comp.positive_quality_control and comp.review_3 is None):
                    to_be_removed.append(r_ann)
                    break
        for x in to_be_removed:
            review_comparisons_map.pop(x)

    def _filter_by_quality_control(self, reviews_comparisons):
        return [rc for rc in reviews_comparisons if rc.positive_quality_control]

    def _get_final_review(self, reviews_comparison_obj):
        if reviews_comparison_obj.review_3:
            return reviews_comparison_obj.review_3
        else:
            return reviews_comparison_obj.review_1

    def _get_final_reviews_map(self, case):
        review_comparisons = ReviewsComparison.objects.filter(
            review_1__slide__in=(case.slides.all())
        )
        rc_map = dict()
        for rc in review_comparisons:
            rc_map.setdefault(rc.review_1.rois_review_step.rois_annotation, []).append(rc)
        for ann in rc_map.keys():
            if not ann.clinical_annotations_completed():
                rc_map.pop(ann)
        self._filter_not_compared(rc_map)
        for r_ann in rc_map.keys():
            rc_map[r_ann] = self._filter_by_quality_control(rc_map[r_ann])
        reviews_map = dict()
        for r_ann, rcs in rc_map.iteritems():
            for rc in rcs:
                reviews_map.setdefault(r_ann, []).append(self._get_final_review(rc))
        logger.info(reviews_map)
        return reviews_map

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
                continue
            for c_ann in core_annotations:
                primary_gleason_scores[c_ann.primary_gleason] += 1
                secondary_gleason_scores.add(c_ann.secondary_gleason)
        if len(primary_gleason_scores) == 0 and len(secondary_gleason_scores) == 0:
            return dict()
        return {
            'primary_score': self._get_max(primary_gleason_scores),
            'secondary_score': max(secondary_gleason_scores)
        }

    def _get_scores(self, reviews_map):
        scores = dict()
        for (r_ann_obj, c_ann_objs) in reviews_map.iteritems():
            oscore = self._get_overall_score(c_ann_objs)
            if len(oscore) > 0:
                scores[r_ann_obj.label] = oscore
        return scores

    def get(self, request, case, format=None):
        case_obj = self._get_case(case)
        reviews_map = self._get_final_reviews_map(case_obj)
        if len(reviews_map) == 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        scores = self._get_scores(reviews_map)
        if len(scores) == 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(scores, status=status.HTTP_200_OK)


class CaseReviewResultsDetails(CaseReviewResults):

    def _get_details(self, clinical_annotation_steps):
        clinical_annotation_details = dict()
        for step in clinical_annotation_steps:
            clinical_annotation_details[step.slide.id] = [
                {
                    'core_label': core_ann.core.label,
                    'primary_gleason_score': core_ann.primary_gleason,
                    'secondary_gleason_score': core_ann.secondary_gleason
                } for core_ann in step.core_annotations.all()
            ]
        return clinical_annotation_details

    def _get_scores(self, reviews_map):
        reviews_scores = dict()
        for r_ann_obj, c_ann_objs in reviews_map.iteritems():
            reviews_scores[r_ann_obj.label] = {
                'overall_score': self._get_overall_score(c_ann_objs),
                'slides_details': self._get_details(c_ann_objs)
            }
        return reviews_scores
