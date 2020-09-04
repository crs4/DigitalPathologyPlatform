#  Copyright (c) 2020, CRS4
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
from reviews_manager.models import ClinicalAnnotationStep
from django.contrib.auth.models import User

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help= """
    """

    def add_arguments(self, parser):
        parser.add_argument('--steps-list', dest='steps_list', type=str, required=True,
                            help='A file containing the labels of the steps that will be reopened')
        parser.add_argument('--delete-annotations', dest='delete_annotations', action='store_true',
                            help='Delete clinical annotations related to reopened steps')
        parser.add_argument('--new-reviewer', dest='new_reviewer', type=str, required=False,
                            default=None, help='The username of the new reviewer for the reopened steps (optional)')

    def _load_user(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            logger.error('There is no user with username %s', username)
            raise CommandError('There is no user with username %s' % username)

    def _load_annotation_steps(self, steps_list):
        with open(steps_list) as f:
            steps_labels = [r.replace('\n', '') for r in f.readlines()]
        annotation_steps = ClinicalAnnotationStep.objects.filter(label__in=steps_labels)
        logger.info('Loaded %d clinical annotation steps (of %d in the list)',
                    len(annotation_steps), len(steps_labels))
        return annotation_steps

    def _assign_new_reviewer(self, clinical_annotations, new_reviewer):
        logger.info('Assigning reviewer %s to clinical annotations', new_reviewer.username)
        for c in clinical_annotations:
            c.reviewer = new_reviewer
            c.save()

    def _reopen_annotation_steps(self, steps, delete_annotations=False, new_reviewer=None):
        logger.info('Reopening clinical annotation steps')
        clinical_annotations = set()
        for s in steps:
            if new_reviewer:
                clinical_annotations.add(s.clinical_annotation)
            s.reopen(delete_annotations)
        if len(clinical_annotations) > 0:
            logger.info('Assigning new reviewer to %d clinical annotations', len(clinical_annotations))
            self._assign_new_reviewer(clinical_annotations, new_reviewer)

    def handle(self, *args, **opts):
        logger.info('== Starting job ==')
        if opts['new_reviewer']:
            new_rev = self._load_user(opts['new_reviewer'])
        else:
            new_rev = None
        steps = self._load_annotation_steps(opts['steps_list'])
        self._reopen_annotation_steps(steps, opts['delete_annotations'], new_rev)
        logger.info('== Job completed ==')
