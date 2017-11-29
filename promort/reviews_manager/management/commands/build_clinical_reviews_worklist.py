from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from promort.settings import DEFAULT_GROUPS
from slides_manager.models import SlideQualityControl
from reviews_manager.models import ROIsAnnotation, ClinicalAnnotation, ClinicalAnnotationStep, ReviewsComparison

from uuid import uuid4
import logging, random
from datetime import datetime

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = 'build second reviewers worklist based on existing ROIs annotations'

    def _get_clinical_manager_users(self):
        clinical_managers_group = Group.objects.get(name=DEFAULT_GROUPS['clinical_manager']['name'])
        return clinical_managers_group.user_set.all()

    def _get_rois_annotations_list(self):
        linked_annotations = [ca.rois_review.label for ca in ClinicalAnnotation.objects.all()]
        return ROIsAnnotation.objects.exclude(label__in=linked_annotations)

    def _select_clinical_reviewers(self, rois_annotation, clinical_managers):
        if rois_annotation.reviewer in clinical_managers:
            reviewer_1 = rois_annotation.reviewer
        else:
            reviewer_1 = random.choice(clinical_managers)
        reviewer_2 = random.choice(clinical_managers)
        while reviewer_2 == reviewer_1:
            reviewer_2 = random.choice(clinical_managers)
        logger.info('REVIEWER 1: %s --- REVIEWER 2: %s', reviewer_1.username, reviewer_2.username)
        return reviewer_1, reviewer_2

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
            adequate_slide = rois_annotation_step_obj.slide_quality_control.adequate_slide
        except SlideQualityControl.DoesNotExist:
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

    def _create_reviews_comparison(self, review_step_1_obj, review_step_2_obj):
        reviews_comparison_obj = ReviewsComparison(review_1=review_step_1_obj, review_2=review_step_2_obj)
        if review_step_1_obj.is_completed() and review_step_2_obj.is_completed():
            logger.info('Bad quality control, closing and marking Reviews Comparison object')
            reviews_comparison_obj.start_date = datetime.now()
            reviews_comparison_obj.close(False, False)
        reviews_comparison_obj.save()
        logger.info('Create Reviews Comparison for Clinical Annotation Steps %s and %s',
                    review_step_1_obj.label, review_step_2_obj.label)
        return reviews_comparison_obj

    def handle(self, *args, **opts):
        logger.info('=== Starting clinical annotations worklist creation ===')
        clinical_annotations_manager = self._get_clinical_manager_users()
        if len(clinical_annotations_manager) < 2:
            raise CommandError('There must be at least 2 users with Clinical Annotations Manager role')
        rois_annotations = self._get_rois_annotations_list()
        if len(rois_annotations) == 0:
            logger.info('There are no ROIs Annotations to process')
        for r_ann in rois_annotations:
            reviewer_1, reviewer_2 = self._select_clinical_reviewers(r_ann, clinical_annotations_manager)
            cl_ann_1 = self._create_clinical_annotation(r_ann, reviewer_1)
            cl_ann_2 = self._create_clinical_annotation(r_ann, reviewer_2)
            for annotation_step in r_ann.steps.all():
                cl_ann_1_step = self._create_clinical_annotation_step(cl_ann_1, annotation_step)
                cl_ann_2_step = self._create_clinical_annotation_step(cl_ann_2, annotation_step)
                self._create_reviews_comparison(cl_ann_1_step, cl_ann_2_step)
        logger.info('=== Clinical annotation worklist creation completed ===')
