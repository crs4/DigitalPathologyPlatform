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

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from promort.settings import DEFAULT_GROUPS
from slides_manager.models import SlideEvaluation
from reviews_manager.models import ROIsAnnotation, ClinicalAnnotation, ClinicalAnnotationStep, ReviewsComparison

from uuid import uuid4
import logging, random
from datetime import datetime

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = 'build second reviewers worklist based on existing ROIs annotations'

    def add_arguments(self, parser):
        parser.add_argument('--reviewers-count', dest='reviewers_count', type=int, default=1,
                            help='the number of clinical reviews created for each ROIs annotation')

    def _get_clinical_manager_users(self):
        clinical_managers_group = Group.objects.get(name=DEFAULT_GROUPS['clinical_manager']['name'])
        return clinical_managers_group.user_set.all()

    def _get_rois_annotations_list(self):
        linked_annotations = [ca.rois_review.label for ca in ClinicalAnnotation.objects.all()]
        return ROIsAnnotation.objects.exclude(label__in=linked_annotations)

    def _select_clinical_reviewers(self, rois_annotation, clinical_managers, reviewers_count):
        if reviewers_count >= len(clinical_managers):
            return clinical_managers
        else:
            reviewers = []
            # by default, assign the clinical annotation to the reviewers that created the ROIs (if enabled)
            if rois_annotation.reviewer in clinical_managers:
                reviewers.append(rois_annotation.reviewer)
            while len(reviewers) < reviewers_count:
                r = random.choice(clinical_managers)
                while r in reviewers:
                    r = random.choice(clinical_managers)
                reviewers.append(r)
            return reviewers

    def _create_clinical_annotation(self, rois_annotation_obj, reviewer_obj):
        logger.info('Assigning review to user %s', reviewer_obj.username)
        if reviewer_obj == rois_annotation_obj.reviewer:
            annotation_label = rois_annotation_obj.label
        else:
            annotation_label = uuid4().hex
        clinical_annotation_obj = ClinicalAnnotation(label=annotation_label, reviewer=reviewer_obj,
                                                     case=rois_annotation_obj.case, rois_review=rois_annotation_obj)
        clinical_annotation_obj.save()
        logger.info('Saved Clinical Annotation with label %s', clinical_annotation_obj.label)
        return clinical_annotation_obj

    def _get_annotation_step_label(self, annotation_label, slide_label):
        slide_index = slide_label.split('-')[-1]
        return '%s-%s' % (annotation_label, slide_index)

    def _create_clinical_annotation_step(self, clinical_annotation_obj, rois_annotation_step_obj):
        annotation_step_obj = ClinicalAnnotationStep(
            label=self._get_annotation_step_label(clinical_annotation_obj.label, rois_annotation_step_obj.slide.id),
            clinical_annotation=clinical_annotation_obj, slide=rois_annotation_step_obj.slide,
            rois_review_step=rois_annotation_step_obj
        )
        # check ROIs Annotation Step quality control
        try:
            adequate_slide = rois_annotation_step_obj.slide_evaluation.adequate_slide
        except SlideEvaluation.DoesNotExist:
            adequate_slide = True
        if not adequate_slide:
            logger.info('BAD QUALITY CONTROL')
            # start clinical annotation object
            if not clinical_annotation_obj.is_started():
                logger.info('Starting clinical annotation')
                clinical_annotation_obj.start_date = datetime.now()
                clinical_annotation_obj.save()
            # start and close clinical annotation step
            logger.info('Opening and closing clinical annotation step')
            annotation_step_obj.start_date = datetime.now()
            annotation_step_obj.completion_date = datetime.now()
            if clinical_annotation_obj.can_be_closed():
                logger.info('Closing clinical annotation')
                clinical_annotation_obj.completion_date = datetime.now()
                clinical_annotation_obj.save()
        annotation_step_obj.save()
        logger.info('Saved new Clinical Annotation Step with label %s', annotation_step_obj.label)
        return annotation_step_obj

    # def _create_reviews_comparison(self, review_step_1_obj, review_step_2_obj):
    #     reviews_comparison_obj = ReviewsComparison(review_1=review_step_1_obj, review_2=review_step_2_obj)
    #     if review_step_1_obj.is_completed() and review_step_2_obj.is_completed():
    #         logger.info('Bad quality control, closing and marking Reviews Comparison object')
    #         reviews_comparison_obj.start_date = datetime.now()
    #         reviews_comparison_obj.close(False, False)
    #     reviews_comparison_obj.save()
    #     logger.info('Create Reviews Comparison for Clinical Annotation Steps %s and %s',
    #                 review_step_1_obj.label, review_step_2_obj.label)
    #     return reviews_comparison_obj

    def handle(self, *args, **opts):
        logger.info('=== Starting clinical annotations worklist creation ===')
        reviewers_count = opts['reviewers_count']
        clinical_annotations_manager = self._get_clinical_manager_users()
        if len(clinical_annotations_manager) == 0:
            raise CommandError('There must be at least 1 user with Clinical Annotations Manager role')
        rois_annotations = self._get_rois_annotations_list()
        if len(rois_annotations) == 0:
            logger.info('There are no ROIs Annotations to process')
        for r_ann in rois_annotations:
            logger.info('Processing ROIs Annotation %s', r_ann.label)
            reviewers = self._select_clinical_reviewers(r_ann, clinical_annotations_manager, reviewers_count)
            for r in reviewers:
                c_ann = self._create_clinical_annotation(r_ann, r)
                for r_step in r_ann.steps.all():
                    self._create_clinical_annotation_step(c_ann, r_step)
        logger.info('=== Clinical annotation worklist creation completed ===')
