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
        parser.add_argument('--page_size', dest='page_size', type=int, default=0,
                            help='the number of records retrieved for each page (this will enable pagination)')

    def _dump_data(self, page_size, csv_writer):
        if page_size > 0:
            logger.info('Pagination enabled (%d records for page)', page_size)
            cas_qs = ClinicalAnnotationStep.objects.get_queryset().order_by('creation_date')
            paginator = Paginator(cas_qs, page_size)
            for x in paginator.page_range:
                logger.info('-- page %d --', x)
                page = paginator.page(x)
                for cas in page.object_list:
                    self._dump_row(cas, csv_writer)
        else:
            logger.info('Loading full batch')
            steps = ClinicalAnnotationStep.objects.all()
            for cas in steps:
                self._dump_row(cas, csv_writer)

    def _dump_row(self, step, csv_writer):
        csv_writer.writerow(
            {
                'case_id': step.slide.case.id,
                'slide_id': step.slide.id,
                'roi_review_step_id': step.rois_review_step.label,
                'clinical_annotation_step_id': step.label,
                'creation_date': self._get_formatted_time(step.creation_date),
                'start_date': self._get_formatted_time(step.start_date),
                'completion_date': self._get_formatted_time(step.completion_date),
                'slices_ann_count': step.slice_annotations.count(),
                'cores_ann_count': step.core_annotations.count(),
                'focus_regions_ann_count': step.focus_region_annotations.count(),
                'reviewer': step.clinical_annotation.reviewer.username,
                'rejected': step.rejected,
                'rejection_reason': step.get_rejection_reason_text(),
                'faded_staining': step.faded_staining,
                'out_of_focus': step.out_of_focus,
                'notes': self._get_encoded_note(step)
            }
        )

    def _get_encoded_note(self, step):
        try:
            return step.notes.encode('utf-8').replace('\n', ' ')
        except TypeError:
            return step.notes.replace('\n', ' ')
        except AttributeError:
            return None

    def _get_formatted_time(self, timestamp):
        try:
            return timestamp.strftime('%Y-%m-%d %H:%M:%S')
        except AttributeError:
            return None

    def _export_data(self, out_file, page_size):
        header = ['case_id', 'slide_id', 'roi_review_step_id', 'clinical_annotation_step_id',
                  'creation_date', 'start_date', 'completion_date', 'reviewer',
                  'slices_ann_count', 'cores_ann_count', 'focus_regions_ann_count',
                  'rejected', 'rejection_reason', 'faded_staining', 'out_of_focus', 'notes']
        with open(out_file, 'w') as ofile:
            writer = DictWriter(ofile, delimiter=',', fieldnames=header)
            writer.writeheader()
            self._dump_data(page_size, writer)

    def handle(self, *args, **opts):
        logger.info('=== Starting export job ===')
        self._export_data(opts['output'], opts['page_size'])
        logger.info('=== Data saved to %s ===', opts['output'])
