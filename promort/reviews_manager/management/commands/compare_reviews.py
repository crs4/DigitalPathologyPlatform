from django.core.management.base import BaseCommand
from reviews_manager.models import ReviewsComparison
from clinical_annotations_manager.models import SliceAnnotation, CoreAnnotation,\
    FocusRegionAnnotation

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = 'perform comparison between clinical reviews'

    def _get_processable_reviews_comparisons(self):
        # get all opened ReviewsComparison objects
        review_comparison = ReviewsComparison.objects.filter(completion_date__isnull=True)
        return [rc for rc in review_comparison if rc.can_be_started()]

    def _check_quality_control(self, review1, review2):
        return review1.rois_review_step.slide_quality_control.adequate_slide

    def _check_reviews_rejection(self, review1, review2):
        return review1.rejected or review2.rejected

    def _compare_slice_annotations(self, sl_ann_1, sl_ann_2):
        return True

    def _check_slices(self, review1, review2):
        r1_slices = SliceAnnotation.objects.filter(annotation_step=review1)
        r2_slices = SliceAnnotation.objects.filter(annotation_step=review2)
        slices_map = dict()
        for x in (r1_slices, r2_slices):
            for sl in x:
                slices_map.setdefault(sl.slice.label, []).append(sl)
        for label, annotations in slices_map.iteritems():
            logger.info('Comparing annotations for slice %s', label)
            result = self._compare_slice_annotations(*annotations)
            if not result:
                logger.info('Annotations for slice %s don\'t match', label)
                return False
            else:
                logger.debug('Annotations for slice %s match', label)
        return True

    def _compare_core_annotations(self, cr_ann_1, cr_ann_2):
        return cr_ann_1.primary_gleason == cr_ann_2.primary_gleason \
               and cr_ann_1.secondary_gleason == cr_ann_2.secondary_gleason

    def _check_cores(self, review1, review2):
        r1_cores = CoreAnnotation.objects.filter(annotation_step=review1)
        r2_cores = CoreAnnotation.objects.filter(annotation_step=review2)
        cores_map = dict()
        for x in (r1_cores, r2_cores):
            for cr in x:
                cores_map.setdefault(cr.core.label, []).append(cr)
        for label, annotations in cores_map.iteritems():
            logger.info('Comparing annotations for core %s', label)
            result = self._compare_core_annotations(*annotations)
            if not result:
                logger.info('Annotations for core %s don\'t match', label)
                return False
            else:
                logger.debug('Annotations for core %s match', label)
        return True

    def _compare_focus_region_annotations(self, fr_ann_1, fr_ann_2):
        return True

    def _check_focus_regions(self, review1, review2):
        r1_focus_regions = FocusRegionAnnotation.objects.filter(annotation_step=review1)
        r2_focus_regions = FocusRegionAnnotation.objects.filter(annotation_step=review2)
        focus_regions_map = dict()
        for x in (r1_focus_regions, r2_focus_regions):
            for fr in x:
                focus_regions_map.setdefault(fr.focus_region.label, []).append(fr)
        for label, annotations in focus_regions_map.iteritems():
            logger.info('Comparing annotations for focus region %s', label)
            result = self._compare_focus_region_annotations(*annotations)
            if not result:
                logger.info('Annotations for focus region %s don\'t match', label)
                return False
            else:
                logger.debug('Annotations for focus region %s match', label)
        return True

    def _run_reviews_comparison(self, reviews_comparison_obj):
        review_1 = reviews_comparison_obj.review_1
        review_2 = reviews_comparison_obj.review_2
        # check if slides passed quality control
        qc_passed = self._check_quality_control(review_1, review_2)
        if not qc_passed:
            logger.info('Bad quality for review 1, stopping comparison')
            return False, qc_passed
        # check if at least one of the two reviews was rejected
        rejected = self._check_reviews_rejection(review_1, review_2)
        if rejected:
            logger.info('Al least one review was rejected, stopping comparison')
            return False, qc_passed
        else:
            good_match = self._check_slices(review_1, review_2)
            if good_match:
                good_match = self._check_cores(review_1, review_2)
                if good_match:
                    good_match = self._check_focus_regions(review_1, review_2)
                    if good_match:
                        return True, qc_passed
        return False, qc_passed

    def _close_comparison(self, reviews_comparison_obj, comparison_passed, quality_control_passed):
        reviews_comparison_obj.close(positive_match=comparison_passed,
                                     positive_quality_control=quality_control_passed)

    def handle(self, *args, **opts):
        logger.info('Collecting reviews comparisons that can be processed')
        processable_comparisons = self._get_processable_reviews_comparisons()
        if len(processable_comparisons) > 0:
            logger.info('Processing %d reviews comparisons', len(processable_comparisons))
            for i, comp in enumerate(processable_comparisons):
                logger.info('### Analysing review comparison %d (of %d) ###', i+1, len(processable_comparisons))
                comparison_passed, quality_control_passed = self._run_reviews_comparison(comp)
                logger.info('COMPARISON STATUS --- comparison_passed: %s - quality_control_passed: %s',
                            comparison_passed, quality_control_passed)
                self._close_comparison(comp, comparison_passed, quality_control_passed)
                logger.info('#### Analysis completed ###')
        else:
            logger.info('No reviews comparisons to process, exit')
