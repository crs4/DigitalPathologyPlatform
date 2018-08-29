from django.core.management.base import BaseCommand
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

    def _load_data(self):
        cores = Core.objects.all()
        return cores

    def _export_data(self, data, out_file):
        header = ['case_id', 'slide_id', 'roi_review_step_id', 'parent_slice_id',
                  'core_label', 'core_id', 'creation_date', 'reviewer', 'length', 'area', 'tumor_length',
                  'positive_core', 'normal_tissue_percentage']
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
                        'normal_tissue_percentage': core.get_normal_tissue_percentage()
                    }
                )

    def handle(self, *args, **opts):
        logger.info('=== Starting export job ===')
        cores = self._load_data()
        self._export_data(cores, opts['output'])
        logger.info('=== Data saved to %s ===', opts['output'])
