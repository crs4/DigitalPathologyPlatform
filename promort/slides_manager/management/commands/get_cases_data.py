from django.core.management.base import BaseCommand
from slides_manager.models import Case

from csv import DictWriter

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    Export existing Cases data to CSV
    """

    def add_arguments(self, parser):
        parser.add_argument('--output_file', dest='output', type=str, required=True,
                            help='path of the output CSV file')

    def _load_data(self):
        cases = Case.objects.all()
        return cases

    def _get_laboratory_label(self, case):
        try:
            return case.laboratory.label
        except AttributeError:
            return None

    def _export_data(self, data, out_file):
        header = ['case_id', 'laboratory', 'slides_count']
        with open(out_file, 'w') as ofile:
            writer = DictWriter(ofile, delimiter=',', fieldnames=header)
            writer.writeheader()
            for case in data:
                lab = self._get_laboratory_label(case)
                writer.writerow(
                    {
                        'case_id': case.id,
                        'laboratory': lab,
                        'slides_count': case.slides.count()
                    }
                )

    def handle(self, *args, **opts):
        logger.info('=== Starting export job ===')
        cases = self._load_data()
        self._export_data(cases, opts['output'])
        logger.info('=== Data saved to %s ===', opts['output'])
