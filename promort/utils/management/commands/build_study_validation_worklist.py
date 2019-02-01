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
from django.contrib.auth.models import Group, User
from django.db import IntegrityError
from promort.settings import DEFAULT_GROUPS
from slides_manager.models import Case
from reviews_manager.models import ROIsAnnotation, ROIsAnnotationStep, \
    ClinicalAnnotation, ClinicalAnnotationStep

from uuid import uuid4
import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        parser.add_argument('--reviewer', dest='reviewer', type=str,
                            help='create reviews list only for this user')
        parser.add_argument('--allow-duplicated', action='store_true', dest='allow_duplicated',
                            help='create worklist even for cases and slides that already have a related review')

    def _get_users(self):
        # get users that belong to the ROIS MANAGERS group
        rois_manager_group = Group.objects.get(name=DEFAULT_GROUPS['rois_manager']['name'])
        return rois_manager_group.user_set.all()

    def _get_user(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    def _get_cases_list(self):
        return Case.objects.all()

    def _get_slides_list(self, case):
        return case.slides.all()

    def _get_roi_annotations(self, case_obj, reviewer_obj, allow_duplicated=False):
        if not allow_duplicated:
            annotations = ROIsAnnotation.objects.filter(case=case_obj, reviewer=reviewer_obj)
            if len(annotations) > 0:
                logger.info('Found %d ROIsAnnotation for case %s and reviewer %s', len(annotations),
                            case_obj.id, reviewer_obj.username)
                return annotations
            else:
                logger.info('There are no ROIsAnnotation for case %s and reviewer %s, creating new one',
                            case_obj.id, reviewer_obj.username)
        else:
            logger.info('Duplication allowed, creating new ROIsAnnotation for case %s and reviewer %s',
                        case_obj.id, reviewer_obj.username)
        annotation = ROIsAnnotation(case=case_obj, reviewer=reviewer_obj, label=uuid4().hex)
        annotation.save()
        return [annotation]

    def _get_annotation_step_label(self, annotation_label, slide_label):
        slide_index = slide_label.split('-')[-1]
        return '%s-%s' % (annotation_label, slide_index)

    def _get_roi_annotation_step(self, slide_obj, roi_annotation_obj):
        try:
            annotation_step = ROIsAnnotationStep(
                rois_annotation=roi_annotation_obj, slide=slide_obj,
                label=self._get_annotation_step_label(roi_annotation_obj.label, slide_obj.id)
            )
            annotation_step.save()
            logger.info('Created new ROIsAnnotationStep for slide %s', slide_obj.id)
        except IntegrityError:
            annotation_step = ROIsAnnotationStep.objects.get(rois_annotation=roi_annotation_obj, slide=slide_obj)
            logger.info('A ROIsAnnotationStep for slide %s already exist', slide_obj.id)
        return annotation_step

    def _get_clinical_annotation(self, case_obj, reviewer_obj, roi_annotation_obj):
        try:
            annotation = ClinicalAnnotation.objects.get(reviewer=reviewer_obj, rois_review=roi_annotation_obj)
            logger.info('Found ClinicalAnnotation for ROIsAnnotation %s', roi_annotation_obj.label)
        except ClinicalAnnotation.DoesNotExist:
            logger.info('There is no ClinicalAnnotation for ROIsAnnotation %s, creating one', roi_annotation_obj.label)
            annotation = ClinicalAnnotation(label=roi_annotation_obj.label, reviewer=reviewer_obj, case=case_obj,
                                            rois_review=roi_annotation_obj)
            annotation.save()
        return annotation

    def _get_clinical_annotation_step(self, clinical_annotation_obj, rois_annotation_step_obj):
        try:
            ClinicalAnnotationStep.objects.get(clinical_annotation=clinical_annotation_obj,
                                               rois_review_step=rois_annotation_step_obj)
            logger.info('Found a ClinicalAnnotationStep for ClinicalAnnotation %s and Slide %s',
                        clinical_annotation_obj.label, rois_annotation_step_obj.slide.id)
        except ClinicalAnnotationStep.DoesNotExist:
            logger.info('There is no ClinicalAnnotationsStep %s and Slide %s, creating one',
                        clinical_annotation_obj.label, rois_annotation_step_obj.slide.id)
            annotation_step = ClinicalAnnotationStep(
                label=rois_annotation_step_obj.label,
                clinical_annotation=clinical_annotation_obj,
                slide=rois_annotation_step_obj.slide,
                rois_review_step=rois_annotation_step_obj
            )
            annotation_step.save()

    def handle(self, *args, **opts):
        logger.info('=== Starting worklist creation ===')
        if opts['reviewer']:
            logger.info('Creating worklist for user %s', opts['reviewer'])
            reviewers = [self._get_user(opts['reviewer'])]
        else:
            logger.info('No reviewer specified, creating worklist for all users in ROIs Managers group')
            reviewers = self._get_users()

        if len(reviewers) == 0:
            raise CommandError('There are no reviewers that can be used to create worklist(s)')

        for reviewer in reviewers:
            logger.info('## Building worklist for user %s', reviewer.username)
            for case in self._get_cases_list():
                # BUILD ROIS ANNOTATIONS WORKFLOW
                roi_annotations = self._get_roi_annotations(case, reviewer, opts['allow_duplicated'])
                for roi_annotation in roi_annotations:
                    roi_annotation_steps = []
                    for slide in self._get_slides_list(case):
                        roi_annotation_steps.append(self._get_roi_annotation_step(slide, roi_annotation))
                    # BUILD CLINICAL ANNOTATIONS WORKFLOW
                    clinical_annotation = self._get_clinical_annotation(case, reviewer, roi_annotation)
                    for roi_annotation_step in roi_annotation_steps:
                        self._get_clinical_annotation_step(clinical_annotation, roi_annotation_step)
            logger.info('## Done with worklist for reviewer %s', reviewer.username)
        logger.info('=== Job completed ===')
