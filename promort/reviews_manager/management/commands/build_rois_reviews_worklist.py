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
from django.db import IntegrityError
from promort.settings import DEFAULT_GROUPS
from slides_manager.models import Case
from reviews_manager.models import ROIsAnnotation, ROIsAnnotationStep

from csv import DictReader
from uuid import uuid4
import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = 'build ROIs reviews worklist based on the existing cases and slides'

    def add_arguments(self, parser):
        parser.add_argument('--worklist-file', dest='worklist', type=str, default=None,
                            help='a CSV file containing the worklist, if not present reviews will be assigned randomly')
        parser.add_argument('--allow-duplicated', action='store_true', dest='allow_duplicated',
                            help='create worklist even for cases and slides that already have a related review')

    def _get_rois_manager_users(self):
        rois_manager_group = Group.objects.get(name=DEFAULT_GROUPS['rois_manager']['name'])
        return rois_manager_group.user_set.all()

    def _get_rois_manager_map(self):
        rois_managers = self._get_rois_manager_users()
        return dict((u.username, u) for u in rois_managers)

    def _get_cases_list(self):
        return Case.objects.all()

    def _get_cases_map(self):
        cases = self._get_cases_list()
        return dict((c.id, c) for c in cases)

    def _create_rois_annotation(self, case_obj, reviewer_obj):
        annotation_obj = ROIsAnnotation(case=case_obj, reviewer=reviewer_obj,
                                        label=uuid4().hex)
        annotation_obj.save()
        logger.info('Saved new ROIs Annotation with label %s and assigned to %s',
                    annotation_obj.label, reviewer_obj.username)
        return annotation_obj

    def _get_or_create_rois_annotation(self, case_obj, reviewer_obj):
        annotation_objs = ROIsAnnotation.objects.filter(case=case_obj, reviewer=reviewer_obj)
        if len(annotation_objs) > 0:
            logger.info('There are already %d ROIs Annotations for case %s assigned to user %s',
                        len(annotation_objs), case_obj.id, reviewer_obj.username)
            return annotation_objs
        else:
            logger.info('No ROIs Annotation found, creating a new one')
            return [self._create_rois_annotation(case_obj, reviewer_obj)]

    def _get_annotation_step_label(self, annotation_label, slide_label):
        slide_index = slide_label.split('-')[-1]
        return '%s-%s' % (annotation_label, slide_index)

    def _create_rois_annotation_step(self, rois_annotation_obj, slide_obj):
        annotation_step_obj = ROIsAnnotationStep(
            rois_annotation=rois_annotation_obj, slide=slide_obj,
            label=self._get_annotation_step_label(rois_annotation_obj.label, slide_obj.id)
        )
        try:
            annotation_step_obj.save()
            logger.info('Saved new ROIs Annotation Step with label %s', annotation_step_obj.label)
        except IntegrityError:
            annotation_step_obj = ROIsAnnotationStep.objects.get(rois_annotation=rois_annotation_obj, slide=slide_obj)
            logger.info('There is already a ROIs Annotation Step object (label %s)', annotation_step_obj.label)
        return annotation_step_obj

    def _create_case_annotation(self, case, reviewer, allow_duplicated):
        if allow_duplicated:
            annotation_objs = [self._create_rois_annotation(case, reviewer)]
        else:
            annotation_objs = self._get_or_create_rois_annotation(case, reviewer)
        for slide in case.slides.all():
            logger.info('Processing slide %s', slide.id)
            for annotation_obj in annotation_objs:
                logger.info('Creating steps for ROIs Annotation %s', annotation_obj.label)
                self._create_rois_annotation_step(annotation_obj, slide)

    def create_random_worklist(self, allow_duplicated):
        logger.info('Creating RANDOM worklist')
        rois_managers = self._get_rois_manager_users()
        cases = self._get_cases_list()
        for i, case in enumerate(cases):
            logger.info('Processing case %s', case.id)
            self._create_case_annotation(case, rois_managers[i % len(rois_managers)], allow_duplicated)

    def create_worklist_from_file(self, worklist_file, allow_duplicated):
        with open(worklist_file) as f:
            reader = DictReader(f)
            cases_map = self._get_cases_map()
            reviewers_map = self._get_rois_manager_map()
            for row in reader:
                logger.info('Processing case %s and assigning to reviewers %s', row['case_id'], row['reviewer'])
                if row['case_id'] not in cases_map:
                    logger.error('Case with ID %s is not on the system', row['case_id'])
                    continue
                if row['reviewer'] not in reviewers_map:
                    logger.error('There is no reviewer with username %s', row['reviewer'])
                    continue
                self._create_case_annotation(cases_map[row['case_id']], reviewers_map[row['reviewer']],
                                             allow_duplicated)

    def handle(self, *args, **opts):
        logger.info('=== Starting ROIs worklist creation ===')
        worklist_file = opts['worklist']
        allow_duplicated = opts['allow_duplicated']
        if worklist_file:
            self.create_worklist_from_file(worklist_file, allow_duplicated)
        else:
            self.create_random_worklist(allow_duplicated)
        logger.info('=== ROIs worklist creation completed ===')
