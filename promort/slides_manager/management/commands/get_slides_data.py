from django.core.management.base import BaseCommand
from slides_manager.models import Slide

from csv import DictWriter

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    Export existing Slides data to CSV
    """

    def add_arguments(self, parser):
        parser.add_argument('--output_file', dest='output', type=str, required=True,
                            help='path of the output CSV file')

    def _load_data(self):
        slides = Slide.objects.all()
        return slides

    def _export_data(self, data, out_file):
        header = ['case_id', 'slide_id']
        with open(out_file, 'w') as ofile:
            writer = DictWriter(ofile, delimiter=',', fieldnames=header)
            writer.writeheader()
            for slide in data:
                writer.writerow(
                    {
                        'case_id': slide.case.id,
                        'slide_id': slide.id
                    }
                )

    def handle(self, *args, **opts):
        logger.info('=== Starting export job ===')
        slides = self._load_data()
        self._export_data(slides, opts['output'])
        logger.info('=== Data saved to %s ===', opts['output'])
