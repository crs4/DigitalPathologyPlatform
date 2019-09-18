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

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from promort.settings import DEFAULT_GROUPS
from reviews_manager.models import ReviewsComparison
from reviews_manager.models import ClinicalAnnotation, ClinicalAnnotationStep

from uuid import uuid4
import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = 'build third reviewer worklist based on the reviews comparisons status'

    def _get_pending_comparisons(self):
        # get all rejected review comparisons that don't have a related third review order and with
        # a positive quality control
        return ReviewsComparison.objects.filter(positive_match=False, positive_quality_control=True,
                                                review_3__isnull=True)

    def _verify(self, review_comparison_obj):
        # check if review1 and review2 are properly linked to the same rois_annotation step
        assert review_comparison_obj.review_1.rois_review_step == review_comparison_obj.review_2.rois_review_step

    def _get_gold_standard_users(self):
        gold_standard_group = Group.objects.get(name=DEFAULT_GROUPS['gold_standard']['name'])
        return gold_standard_group.user_set.all()

    def _get_clinical_annotation_object(self, rois_review_obj, reviewer):
        try:
            return ClinicalAnnotation.objects.get(rois_review=rois_review_obj, reviewer=reviewer)
        except ClinicalAnnotation.DoesNotExist:
            return None

    def _create_clinical_annotation(self, rois_review_obj, reviewer):
        c_ann_obj = ClinicalAnnotation(
            label=uuid4().hex,
            reviewer=reviewer,
            rois_review=rois_review_obj,
            case=rois_review_obj.case
        )
        c_ann_obj.save()
        return c_ann_obj

    def _get_or_create_clinical_annotation(self, rois_review_obj, reviewer):
        cl_ann = self._get_clinical_annotation_object(rois_review_obj, reviewer)
        if cl_ann is None:
            logger.info('Creating new clinical annotation for user %s', reviewer.username)
            cl_ann = self._create_clinical_annotation(rois_review_obj, reviewer)
        else:
            logger.info('Got clinical annotation %s for user %s', cl_ann.label, reviewer.username)
        return cl_ann

    def _get_clinical_annotation_step_label(self, slide_label, clinical_annotation_label):
        slide_index = slide_label.split('-')[-1].split('.')[0].replace('_', '-')
        return '%s-%s' % (clinical_annotation_label, slide_index)

    def _create_clinical_annotation_step(self, clinical_annotation_obj, rois_review_step_obj):
        c_ann_step_obj = ClinicalAnnotationStep(
            label=self._get_clinical_annotation_step_label(rois_review_step_obj.slide.id,
                                                           clinical_annotation_obj.label),
            slide=rois_review_step_obj.slide,
            clinical_annotation=clinical_annotation_obj,
            rois_review_step=rois_review_step_obj
        )
        c_ann_step_obj.save()
        return c_ann_step_obj

    def _link_clinical_annotation(self, review_comparison_obj, reviewer):
        rois_review_step_obj = review_comparison_obj.review_1.rois_review_step
        rois_review_obj = rois_review_step_obj.rois_annotation
        clinical_annotation_obj = self._get_or_create_clinical_annotation(rois_review_obj, reviewer)
        clinical_annotation_step_obj = self._create_clinical_annotation_step(clinical_annotation_obj,
                                                                             rois_review_step_obj)
        logger.info('Linking new clinical annotation step to reviews comparison object')
        review_comparison_obj.link_review_3(clinical_annotation_step_obj)

    def handle(self, *args, **opts):
        logger.info('Collecting reviews comparisons')
        review_comparisons = self._get_pending_comparisons()
        if len(review_comparisons) > 0:
            logger.info('Processing %d review comparisons', len(review_comparisons))
            gs_users = self._get_gold_standard_users()
            if len(gs_users) > 0:
                logger.info('Retrieved %d users from GOLD STANDARDS group', len(gs_users))
                for i, rc in enumerate(review_comparisons):
                    self._verify(rc)
                    reviewer = gs_users[i % len(gs_users)]
                    self._link_clinical_annotation(rc, reviewer)
            else:
                logger.info('There are no users registered in GOLD STANDARDS group')
        else:
            logger.info('There are no review comparisons that need to be processed')
