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
from reviews_manager.models import ClinicalAnnotationStep

from csv import DictWriter

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    Export existing ClinicalAnnotationStep data to CSV
    """

    def add_arguments(self, parser):
        parser.add_argument('--output_file', dest='output', type=str, required=True,
                            help='path of the output CSV file')

    def _load_data(self):
        annotation_steps = ClinicalAnnotationStep.objects.all()
        return annotation_steps

    def _get_encoded_note(self, step):
        try:
            return step.notes.encode('utf-8').replace('\n', ' ')
        except AttributeError:
            return None

    def _export_data(self, data, out_file):
        header = ['case_id', 'slide_id', 'roi_review_step_id', 'clinical_annotation_step_id',
                  'creation_date', 'start_date', 'completion_date', 'reviewer', 'rejected',
                  'rejection_reason', 'notes']
        with open(out_file, 'w') as ofile:
            writer = DictWriter(ofile, delimiter=',', fieldnames=header)
            writer.writeheader()
            for step in data:
                writer.writerow(
                    {
                        'case_id': step.slide.case.id,
                        'slide_id': step.slide.id,
                        'roi_review_step_id': step.rois_review_step.label,
                        'clinical_annotation_step_id': step.label,
                        'creation_date': step.creation_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'start_date': step.start_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'completion_date': step.completion_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'reviewer': step.clinical_annotation.reviewer.username,
                        'rejected': step.rejected,
                        'rejection_reason': step.get_rejection_reason_text(),
                        'notes': self._get_encoded_note(step)
                    }
                )

    def handle(self, *args, **opts):
        logger.info('=== Starting export job ===')
        annotation_steps = self._load_data()
        self._export_data(annotation_steps, opts['output'])
        logger.info('=== Data saved to %s ===', opts['output'])
