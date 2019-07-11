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
from slides_manager.models import SlideEvaluation

from csv import DictWriter

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    Export existing SlideEvaluation data to CSV
    """

    def add_arguments(self, parser):
        parser.add_argument('--output_file', dest='output', type=str, required=True,
                            help='path of the output CSV file')
        parser.add_argument('--page_size', dest='page_size', type=int, default=0,
                            help='the number of records retrieved for each page (this will enable pagination)')

    def _dump_data(self, page_size, csv_writer):
        if page_size > 0:
            logger.info('Pagination enabled (%d records for page)', page_size)
            se_qs = SlideEvaluation.objects.get_queryset().defer('roi_json').order_by('creation_date')
            paginator = Paginator(se_qs, page_size)
            for x in paginator.page_range:
                logger.info('-- page %d --', x)
                page = paginator.page(x)
                for se in page.object_list:
                    self._dump_row(se, csv_writer)
        else:
            logger.info('Loading full batch')
            slices = SlideEvaluation.objects.all()
            for se in slices:
                self._dump_row(se, csv_writer)

    def _dump_row(self, evaluation, csv_writer):
        csv_writer.writerow(
            {
                'case_id': evaluation.slide.case.id,
                'slide_id': evaluation.slide.id,
                'roi_review_step_id': evaluation.rois_annotation_step.label,
                'staining': evaluation.get_staining_text(),
                'adequate_slide': evaluation.adequate_slide,
                'not_adequacy_reason': evaluation.get_not_adequacy_reason_text(),
                'notes': evaluation.notes,
                'reviewer': evaluation.reviewer.username,
                'acquisition_date': evaluation.acquisition_date.strftime('%Y-%m-%d %H:%M:%S')
            }
        )

    def _export_data(self, out_file, page_size):
        header = ['case_id', 'slide_id', 'roi_review_step_id', 'staining', 'adequate_slide', 'not_adequacy_reason',
                  'notes', 'reviewer', 'acquisition_date']
        with open(out_file, 'w') as ofile:
            writer = DictWriter(ofile, delimiter=',', fieldnames=header)
            writer.writeheader()
            self._dump_data(page_size, writer)

    def handle(self, *args, **opts):
        logger.info('=== Starting export job ===')
        self._export_data(opts['output'], opts['page_size'])
        logger.info('=== Data saved to %s ===', opts['output'])
