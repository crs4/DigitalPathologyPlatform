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

    def _export_data(self, data, out_file):
        header = ['case_id', 'slide_id', 'rois_review_step_id', 'parent_core_id',
                  'focus_region_label', 'focus_region_id', 'creation_date', 'reviewer', 'length',
                  'area', 'cancerous_region', 'core_coverage_percentage']
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
                        'focus_region_label': focus_region.label,
                        'focus_region_id': focus_region.id,
                        'creation_date': focus_region.creation_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'reviewer': focus_region.author.username,
                        'length': focus_region.length,
                        'area': focus_region.area,
                        'cancerous_region': focus_region.cancerous_region,
                        'core_coverage_percentage': focus_region.get_core_coverage_percentage()
                    }
                )

    def handle(self, *args, **opts):
        logger.info('=== Starting export job ===')
        focus_regions = self._load_data()
        self._export_data(focus_regions, opts['output'])
        logger.info('=== Data saved to %s ===', opts['output'])
