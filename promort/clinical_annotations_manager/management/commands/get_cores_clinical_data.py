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
from clinical_annotations_manager.models import CoreAnnotation

from csv import DictWriter

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    Export existing Core clinical data to CSV
    """

    def add_arguments(self, parser):
        parser.add_argument('--output_file', dest='output', type=str, required=True,
                            help='path of the output CSV file')

    def _load_data(self):
        core_annotations = CoreAnnotation.objects.all()
        return core_annotations

    def _export_data(self, data, out_file):
        header = ['case_id', 'slide_id', 'rois_review_step_id', 'clinical_review_step_id', 'reviewer',
                  'core_id', 'core_label', 'creation_date', 'primary_gleason', 'secondary_gleason',
                  'gleason_group_who_16']
        with open(out_file, 'w') as ofile:
            writer = DictWriter(ofile, delimiter=',', fieldnames=header)
            writer.writeheader()
            for core_annotation in data:
                writer.writerow(
                    {
                        'case_id': core_annotation.core.slice.slide.case.id,
                        'slide_id': core_annotation.core.slice.slide.id,
                        'rois_review_step_id': core_annotation.annotation_step.rois_review_step.label,
                        'clinical_review_step_id': core_annotation.annotation_step.label,
                        'reviewer': core_annotation.author.username,
                        'core_id': core_annotation.core.id,
                        'core_label': core_annotation.core.label,
                        'creation_date': core_annotation.creation_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'primary_gleason': core_annotation.primary_gleason,
                        'secondary_gleason': core_annotation.secondary_gleason,
                        'gleason_group_who_16': core_annotation.get_grade_group_text()
                    }
                )

    def handle(self, *args, **opts):
        logger.info('=== Starting export job ===')
        core_annotations = self._load_data()
        self._export_data(core_annotations, opts['output'])
        logger.info('=== Data saved to %s ===', opts['output'])
