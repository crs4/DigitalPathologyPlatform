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

    def _load_data(self, page_size):
        if page_size > 0:
            logger.info('Pagination enabled (%d records for page)', page_size)
            c_qs = Core.objects.get_queryset().defer('roi_json').order_by('label')
            paginator = Paginator(c_qs, page_size)
            cores = list()
            for x in paginator.page_range:
                logger.info('-- page %d --', x)
                page = paginator.page(x)
                cores.extend(page.object_list)
        else:
            logger.info('Loading full batch')
            cores = Core.objects.all()
        return cores

    def _export_data(self, data, out_file):
        header = ['case_id', 'slide_id', 'roi_review_step_id', 'parent_slice_id',
                  'core_label', 'core_id', 'creation_date', 'reviewer', 'length', 'area', 'tumor_length',
                  'positive_core', 'normal_tissue_percentage', 'total_tumor_area']
        with open(out_file, 'w') as ofile:
            writer = DictWriter(ofile, delimiter=',', fieldnames=header)
            writer.writeheader()
            for core in data:
                writer.writerow(
                    {
                        'case_id': core.slice.slide.case.id,
                        'slide_id': core.slice.slide.id,
                        'roi_review_step_id': core.slice.annotation_step.label,
                        'parent_slice_id': core.slice.id,
                        'core_label': core.label,
                        'core_id': core.id,
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

    def handle(self, *args, **opts):
        logger.info('=== Starting export job ===')
        cores = self._load_data(opts['page_size'])
        self._export_data(cores, opts['output'])
        logger.info('=== Data saved to %s ===', opts['output'])
