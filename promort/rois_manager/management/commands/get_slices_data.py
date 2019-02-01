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
from rois_manager.models import Slice

from csv import DictWriter

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    Export existing Slices data to CSV (ROIs data only)
    """

    def add_arguments(self, parser):
        parser.add_argument('--output_file', dest='output', type=str, required=True,
                            help='path of the output CSV file')

    def _load_data(self):
        slices = Slice.objects.all()
        return slices

    def _export_data(self, data, out_file):
        header = ['case_id', 'slide_id', 'roi_review_step_id', 'slice_label', 'slice_id', 'creation_date',
                  'reviewer', 'positive_slice', 'positive_cores', 'total_cores']
        with open(out_file, 'w') as ofile:
            writer = DictWriter(ofile, delimiter=',', fieldnames=header)
            writer.writeheader()
            for slice in data:
                writer.writerow(
                    {
                        'case_id': slice.slide.case.id,
                        'slide_id': slice.slide.id,
                        'roi_review_step_id': slice.annotation_step.label,
                        'slice_label': slice.label,
                        'slice_id': slice.id,
                        'creation_date': slice.creation_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'reviewer': slice.author.username,
                        'positive_slice': slice.is_positive(),
                        'total_cores': slice.total_cores,
                        'positive_cores': slice.get_positive_cores_count()
                    }
                )

    def handle(self, *args, **opts):
        logger.info('=== Starting export job ===')
        slices = self._load_data()
        self._export_data(slices, opts['output'])
        logger.info('=== Data saved to %s ===', opts['output'])
