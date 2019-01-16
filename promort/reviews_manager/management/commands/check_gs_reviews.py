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
from reviews_manager.models import ReviewsComparison

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = 'check third reviewer\'s worklist and fix it if necessary'

    def add_arguments(self, parser):
        parser.add_argument('--keep_reviews', action='store_true',
                            help='Keep reviews performed by third reviewer even if not necessary')

    def _get_review_comparisons(self):
        return ReviewsComparison.objects.filter(positive_match=False, positive_quality_control=True)

    def _delete_review(self, clinical_annotation):
        if len(clinical_annotation.steps.all()) == 0:
            clinical_annotation.delete()
            logger.info('Clinical annotation %s deleted', clinical_annotation.label)

    def _delete_gs_review_step(self, clinical_annotation_step):
        fr_ann = clinical_annotation_step.focus_region_annotations.all()
        logger.info('Deleting %d focus region annotations', len(fr_ann))
        fr_ann.delete()
        c_ann = clinical_annotation_step.core_annotations.all()
        logger.info('Deleting %d core annotations', len(c_ann))
        c_ann.delete()
        s_ann = clinical_annotation_step.slice_annotations.all()
        logger.info('Deleting %d slice annotations', len(s_ann))
        s_ann.delete()
        c_ann = clinical_annotation_step.clinical_annotation
        clinical_annotation_step.delete()
        logger.info('Clinical annotation step %s deleted', clinical_annotation_step.label)
        self._delete_review(c_ann)

    def _check_and_fix(self, rc_object, keep_review):
        if not rc_object.review_1.rois_review_step.is_positive():
            logger.info('### ReviewComparison object %d --- NEED TO FIX! ###', rc_object.id)
            if rc_object.review_3 is not None and not keep_review:
                r3_obj = rc_object.review_3
                logger.info('-- Clearing reviews step %s --', r3_obj.label)
                # unlink to prevent delete protection error
                rc_object.review_3 = None
                rc_object.save()
                # delete clinical annotation step
                self._delete_gs_review_step(r3_obj)
            rc_object.positive_match = True
            logger.info('Setting RC object positive_match to True')
            rc_object.save()

    def handle(self, *args, **opts):
        logger.info('Collecting ReviewsComparison objects')
        r_comp = self._get_review_comparisons()
        logger.info('Retrieved %d objects', len(r_comp))
        for rc in r_comp:
            self._check_and_fix(rc, opts['keep_reviews'])
