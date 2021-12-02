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
from clinical_annotations_manager.models import FocusRegionAnnotation

from csv import DictWriter

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    Export existing FocusRegion clinical data to CSV
    """

    def add_arguments(self, parser):
        parser.add_argument('--output_file', dest='output', type=str, required=True,
                            help='path of the output CSV file')
        parser.add_argument('--page_size', dest='page_size', type=int, default=0,
                            help='the number of records retrieved for each page (this will enable pagination)')

    def _dump_data(self, page_size, csv_writer):
        if page_size > 0:
            logger.info('Pagination enabled (%d records for page)', page_size)
            fra_qs = FocusRegionAnnotation.objects.get_queryset().order_by('creation_date')
            paginator = Paginator(fra_qs, page_size)
            for x in paginator.page_range:
                logger.info('-- page %d --', x)
                page = paginator.page(x)
                for fra in page.object_list:
                    self._dump_row(fra, csv_writer)
        else:
            focus_region_annotations = FocusRegionAnnotation.objects.all()
            for fra in focus_region_annotations:
                self._dump_row(fra, csv_writer)

    def _dump_row(self, focus_region_annotation, csv_writer):
        try:
            action_start_time = focus_region_annotation.action_start_time.strftime('%Y-%m-%d %H:%M:%S')
        except AttributeError:
            action_start_time = None
        try:
            action_complete_time = focus_region_annotation.action_complete_time.strftime('%Y-%m-%d %H:%M:%S')
        except AttributeError:
            action_complete_time = None
        csv_writer.writerow(
            {
                'case_id': focus_region_annotation.focus_region.core.slice.slide.case.id,
                'slide_id': focus_region_annotation.focus_region.core.slice.slide.id,
                'rois_review_step_id': focus_region_annotation.annotation_step.rois_review_step.label,
                'clinical_review_step_id': focus_region_annotation.annotation_step.label,
                'reviewer': focus_region_annotation.author.username,
                'focus_region_id': focus_region_annotation.focus_region.id,
                'focus_region_label': focus_region_annotation.focus_region.label,
                'core_id': focus_region_annotation.focus_region.core.id,
                'core_label': focus_region_annotation.focus_region.core.label,
                'action_start_time': action_start_time,
                'action_complete_time': action_complete_time,
                'creation_date': focus_region_annotation.creation_date.strftime('%Y-%m-%d %H:%M:%S'),
                'perineural_involvement': focus_region_annotation.perineural_involvement,
                'intraductal_carcinoma': focus_region_annotation.intraductal_carcinoma,
                'ductal_carcinoma': focus_region_annotation.ductal_carcinoma,
                'poorly_formed_glands': focus_region_annotation.poorly_formed_glands,
                'cribriform_pattern': focus_region_annotation.cribriform_pattern,
                'small_cell_signet_ring': focus_region_annotation.small_cell_signet_ring,
                'hypernephroid_pattern': focus_region_annotation.hypernephroid_pattern,
                'mucinous': focus_region_annotation.mucinous,
                'comedo_necrosis': focus_region_annotation.comedo_necrosis,
                'total_gleason_4_area': focus_region_annotation.get_total_gleason_4_area(),
                'gleason_4_percentage': focus_region_annotation.get_gleason_4_percentage()
            }
        )

    def _export_data(self, out_file, page_size):
        header = ['case_id', 'slide_id', 'rois_review_step_id', 'clinical_review_step_id', 'reviewer',
                  'focus_region_id', 'focus_region_label', 'core_id', 'core_label', 'action_start_time',
                  'action_complete_time', 'creation_date', 'perineural_involvement', 'intraductal_carcinoma',
                  'ductal_carcinoma', 'poorly_formed_glands', 'cribriform_pattern', 'small_cell_signet_ring',
                  'hypernephroid_pattern', 'mucinous', 'comedo_necrosis', 'total_gleason_4_area', 'gleason_4_percentage']
        with open(out_file, 'w') as ofile:
            writer = DictWriter(ofile, delimiter=',', fieldnames=header)
            writer.writeheader()
            self._dump_data(page_size, writer)

    def handle(self, *args, **opts):
        logger.info('=== Starting export job ===')
        self._export_data(opts['output'], opts['page_size'])
        logger.info('=== Data saved to %s ===', opts['output'])
