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
from django.core.paginator import Paginator
from clinical_annotations_manager.models import SliceAnnotation

from csv import DictWriter

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    Export existing Slice clinical data to CSV
    """

    def add_arguments(self, parser):
        parser.add_argument('--output_file', dest='output', type=str, required=True,
                            help='path of the output CSV file')
        parser.add_argument('--page_size', dest='page_size', type=int, default=0,
                            help='the number of records retrieved for each page (this will enable pagination)')

    def _dump_data(self, page_size, csv_writer):
        if page_size > 0:
            logger.info('Pagination enabled (%d records for page)', page_size)
            sa_qs = SliceAnnotation.objects.get_queryset().order_by('creation_date')
            paginator = Paginator(sa_qs, page_size)
            for x in paginator.page_range:
                logger.info('-- page %d --', x)
                page = paginator.page(x)
                for sa in page.object_list:
                    self._dump_row(sa, csv_writer)
        else:
            logger.info('Loading full batch')
            slice_annotations = SliceAnnotation.objects.all()
            for sa in slice_annotations:
                self._dump_row(sa, csv_writer)

    def _dump_row(self, slice_annotation, csv_writer):
        try:
            action_start_time = slice_annotation.action_start_time.strftime('%Y-%m-%d %H:%M:%S')
        except AttributeError:
            action_start_time = None
        csv_writer.writerow(
            {
                'case_id': slice_annotation.slice.slide.case.id,
                'slide_id': slice_annotation.slice.slide.id,
                'rois_review_step_id': slice_annotation.annotation_step.rois_review_step.label,
                'clinical_review_step_id': slice_annotation.annotation_step.label,
                'reviewer': slice_annotation.author.username,
                'slice_id': slice_annotation.slice.id,
                'slice_label': slice_annotation.slice.label,
                'action_start_time': action_start_time,
                'creation_date': slice_annotation.creation_date.strftime('%Y-%m-%d %H:%M:%S'),
                'high_grade_pin': slice_annotation.high_grade_pin,
                'pah': slice_annotation.pah,
                'chronic_inflammation': slice_annotation.chronic_inflammation,
                'acute_inflammation': slice_annotation.acute_inflammation,
                'periglandular_inflammation': slice_annotation.periglandular_inflammation,
                'intraglandular_inflammation': slice_annotation.intraglandular_inflammation,
                'stromal_inflammation': slice_annotation.stromal_inflammation
            }
        )

    def _export_data(self, out_file, page_size):
        header = ['case_id', 'slide_id', 'rois_review_step_id', 'clinical_review_step_id', 'reviewer',
                  'slice_id', 'slice_label', 'action_start_time', 'creation_date', 'high_grade_pin', 'pah',
                  'chronic_inflammation', 'acute_inflammation', 'periglandular_inflammation',
                  'intraglandular_inflammation', 'stromal_inflammation']
        with open(out_file, 'w') as ofile:
            writer = DictWriter(ofile, delimiter=',', fieldnames=header)
            writer.writeheader()
            self._dump_data(page_size, writer)

    def handle(self, *args, **opts):
        logger.info('=== Starting export job ===')
        self._export_data(opts['output'], opts['page_size'])
        logger.info('=== Data saved to %s ===', opts['output'])
