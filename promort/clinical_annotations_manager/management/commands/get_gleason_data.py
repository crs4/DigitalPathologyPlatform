#  Copyright (c) 2021, CRS4
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
from clinical_annotations_manager.models import GleasonElement

from csv import DictWriter

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    Export existing Gleason items data to CSV.
    No ROIs are exported, only metadata; to export ROIs use the extract_gleason_elements command.
    """
    
    def add_arguments(self, parser):
        parser.add_argument('--output_file', dest='output', type=str, required=True,
                            help='path of the output CSV file')
        parser.add_argument('--page_size', dest='page_size', type=int, default=0,
                            help='the number of records retrieved for each page (this will enable pagination)')
    
    def _dump_row(self, gleason_element, csv_writer):
        try:
            creation_start_date = gleason_element.creation_start_date.strftime('%Y-%m-%d %H:%M:%S')
        except AttributeError:
            creation_start_date = None
        fr_ann = gleason_element.focus_region_annotation
        csv_writer.writerow(
            {
                'case_id': fr_ann.focus_region.core.slice.slide.case.id,
                'slide_id': fr_ann.focus_region.core.slice.slide.id,
                'rois_review_step_id': fr_ann.annotation_step.rois_review_step.label,
                'clinical_review_step_id': fr_ann.annotation_step.label,
                'reviewer': fr_ann.author.username,
                'focus_region_id': fr_ann.focus_region.id,
                'focus_region_label': fr_ann.focus_region.label,
                'core_id': fr_ann.focus_region.core.id,
                'core_label': fr_ann.focus_region.core.label,
                'gleason_element_id': gleason_element.id,
                'gleason_type': gleason_element.gleason_type,
                'creation_start_date': creation_start_date,
                'creation_date': gleason_element.creation_date.strftime('%Y-%m-%d %H:%M:%S')
            }
        )
    
    def _dump_data(self, page_size, csv_writer):
        if page_size > 0:
            logger.info('Pagination enabled (%d records for page)', page_size)
            ge_qs = GleasonElement.objects.get_queryset().order_by('creation_date')
            paginator = Paginator(ge_qs, page_size)
            for x in paginator.page_range:
                logger.info(f'-- page {x} --')
                page = paginator.page(x)
                for ge in page.object_list:
                    self._dump_row(ge, csv_writer)
        else:
            logger.info('Loading full batch')
            gleason_elements = GleasonElement.objects.all()
            for ge in gleason_elements:
                self._dump_row(ge, csv_writer)
    
    def _export_data(self, out_file, page_size):
        header = ['case_id', 'slide_id', 'rois_review_step_id', 'clinical_review_step_id', 'reviewer', 'focus_region_id',
                  'focus_region_label', 'core_id', 'core_label', 'gleason_element_id', 'gleason_type',
                  'creation_start_date', 'creation_date']
        with open(out_file, 'w') as ofile:
            writer = DictWriter(ofile, delimiter=',', fieldnames=header)
            writer.writeheader()
            self._dump_data(page_size, writer)
    
    def handle(self, *args, **opts):
        logger.info('=== Starting export job ===')
        self._export_data(opts['output'], opts['page_size'])
        logger.info('=== Data saved to {0} ==='.format(opts['output']))
