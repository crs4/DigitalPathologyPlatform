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
from rois_manager.models import FocusRegion

from csv import DictWriter

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    Export existing FocusRegions data to CSV
    """

    def add_arguments(self, parser):
        parser.add_argument('--output_file', dest='output', type=str, required=True,
                            help='path of the output CSV file')

    def _load_data(self):
        focus_regions = FocusRegion.objects.all()
        return focus_regions

    def _get_region_tissue_status(self, focus_region):
        if focus_region.is_cancerous_region():
            return 'TUMOR'
        elif focus_region.is_stressed_region():
            return 'STRESSED'
        elif focus_region.is_normal_region():
            return 'NORMAL'

    def _export_data(self, data, out_file):
        header = ['case_id', 'slide_id', 'rois_review_step_id', 'parent_core_id', 'parent_core_label',
                  'focus_region_label', 'focus_region_id', 'creation_date', 'reviewer', 'length',
                  'area', 'tissue_status', 'core_coverage_percentage']
        with open(out_file, 'w') as ofile:
            writer = DictWriter(ofile, delimiter=',', fieldnames=header)
            writer.writeheader()
            for focus_region in data:
                writer.writerow(
                    {
                        'case_id': focus_region.core.slice.slide.case.id,
                        'slide_id': focus_region.core.slice.slide.id,
                        'rois_review_step_id': focus_region.core.slice.annotation_step.label,
                        'parent_core_id': focus_region.core.id,
                        'parent_core_label': focus_region.core.label,
                        'focus_region_label': focus_region.label,
                        'focus_region_id': focus_region.id,
                        'creation_date': focus_region.creation_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'reviewer': focus_region.author.username,
                        'length': focus_region.length,
                        'area': focus_region.area,
                        'tissue_status': self._get_region_tissue_status(focus_region),
                        'core_coverage_percentage': focus_region.get_core_coverage_percentage()
                    }
                )

    def handle(self, *args, **opts):
        logger.info('=== Starting export job ===')
        focus_regions = self._load_data()
        self._export_data(focus_regions, opts['output'])
        logger.info('=== Data saved to %s ===', opts['output'])
