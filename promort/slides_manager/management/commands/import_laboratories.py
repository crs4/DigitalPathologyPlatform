from django.core.management.base import BaseCommand
from slides_manager.models import Laboratory

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    Import laboratories from a text file with one laboratory label per line
    """

    def add_arguments(self, parser):
        parser.add_argument('--labs-list', dest='labs_list', type=str, required=True,
                            help='the file containing the list of the laboratories that will be imported')

    def _get_labs_list(self, labs_file):
        with open(labs_file) as lf:
            return [line.replace('\n', '') for line in lf]

    def _save_lab(self, lab_label):
        _, created = Laboratory.objects.get_or_create(
            label__iexact=lab_label,
            defaults={'label': lab_label}
        )
        if created:
            logger.info('Created Laboratory %s', lab_label)
        else:
            logger.info('Laboratory %s already exists', lab_label)

    def handle(self, *args, **opts):
        logger.info('=== Starting import job ===')
        labs_list = self._get_labs_list(opts['labs_list'])
        for lab in labs_list:
            self._save_lab(lab)
        logger.info('=== Import job completed ===')
