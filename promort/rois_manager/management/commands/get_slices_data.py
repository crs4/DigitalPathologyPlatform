from django.core.management.base import BaseCommand
from rois_manager.models import Slice

from csv import DictWriter

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    Export existing Slices data to CSV (ROIs data only)
    """

    def add_arguments(self, parser):
        parser.add_argument('--output_file', dest='output', type=str, required=True,
                            help='path of the output CSV file')

    def _load_data(self):
        slices = Slice.objects.all()
        return slices

    def _export_data(self, data, out_file):
        header = ['case_id', 'slide_id', 'roi_review_step_id', 'slice_label', 'slice_id',
                  'reviewer', 'positive_slice', 'positive_cores', 'total_cores']
        with open(out_file, 'w') as ofile:
            writer = DictWriter(ofile, delimiter=',', fieldnames=header)
            writer.writeheader()
            for slice in data:
                writer.writerow(
                    {
                        'case_id': slice.slide.case.id,
                        'slide_id': slice.slide.id,
                        'roi_review_step_id': slice.annotation_step.label,
                        'slice_label': slice.label,
                        'slice_id': slice.id,
                        'reviewer': slice.author.username,
                        'positive_slice': slice.is_positive(),
                        'total_cores': slice.total_cores,
                        'positive_cores': slice.get_positive_cores_count()
                    }
                )

    def handle(self, *args, **opts):
        logger.info('=== Starting export job ===')
        slices = self._load_data()
        self._export_data(slices, opts['output'])
        logger.info('=== Data saved to %s ===', opts['output'])
