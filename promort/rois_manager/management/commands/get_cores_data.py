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
from rois_manager.models import Core

from csv import DictWriter

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    Export existing Cores data to CSV (ROIs data only)
    """

    def add_arguments(self, parser):
        parser.add_argument('--output_file', dest='output', type=str, required=True,
                            help='path of the output CSV file')
        parser.add_argument('--page_size', dest='page_size', type=int, default=0,
                            help='the number of records retrieved for each page (this will enable pagination)')

    def _dump_data(self, page_size, csv_writer):
        if page_size > 0:
            logger.info('Pagination enabled (%d records for page)', page_size)
            c_qs = Core.objects.get_queryset().defer('roi_json').order_by('creation_date')
            paginator = Paginator(c_qs, page_size)
            for x in paginator.page_range:
                logger.info('-- page %d --', x)
                page = paginator.page(x)
                for c in page.object_list:
                    self._dump_row(c, csv_writer)
        else:
            logger.info('Loading full batch')
            cores = Core.objects.all()
            for c in cores:
                self._dump_row(c, csv_writer)

    def _dump_row(self, core, csv_writer):
        try:
            action_start_time = core.action_start_time.strftime('%Y-%m-%d %H:%M:%S')
        except AttributeError:
            action_start_time = None
        try:
            action_complete_time = core.action_complete_time.strftime('%Y-%m-%d %H:%M:%S')
        except AttributeError:
            action_complete_time = None
        csv_writer.writerow(
            {
                'case_id': core.slice.slide.case.id,
                'slide_id': core.slice.slide.id,
                'rois_review_step_id': core.slice.annotation_step.label,
                'parent_slice_id': core.slice.id,
                'core_label': core.label,
                'core_id': core.id,
                'action_start_time': action_start_time,
                'action_complete_time': action_complete_time,
                'creation_date': core.creation_date.strftime('%Y-%m-%d %H:%M:%S'),
                'reviewer': core.author.username,
                'length': core.length,
                'area': core.area,
                'tumor_length': core.tumor_length,
                'positive_core': core.is_positive(),
                'normal_tissue_percentage': core.get_normal_tissue_percentage(),
                'total_tumor_area': core.get_total_tumor_area()
            }
        )

    def _export_data(self, out_file, page_size):
        header = ['case_id', 'slide_id', 'rois_review_step_id', 'parent_slice_id', 'core_label', 'core_id',
                  'action_start_time', 'action_complete_time', 'creation_date', 'reviewer', 'length', 'area',
                  'tumor_length', 'positive_core', 'normal_tissue_percentage', 'total_tumor_area']
        with open(out_file, 'w') as ofile:
            writer = DictWriter(ofile, delimiter=',', fieldnames=header)
            writer.writeheader()
            self._dump_data(page_size, writer)

    def handle(self, *args, **opts):
        logger.info('=== Starting export job ===')
        self._export_data(opts['output'], opts['page_size'])
        logger.info('=== Data saved to %s ===', opts['output'])
