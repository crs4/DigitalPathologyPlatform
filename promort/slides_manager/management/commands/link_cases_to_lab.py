from csv import DictReader

from django.core.management.base import BaseCommand
from slides_manager.models import Laboratory, Case

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    """

    def add_arguments(self, parser):
        parser.add_argument('--cases-map', dest='cases_map', type=str, required=True,
                            help='the CSV file containing the mapping of the cases to related laboratories')

    def _get_cases_map(self, cases_file):
        with open(cases_file) as cf:
            reader = DictReader(cf, ['case', 'laboratory'])
            cases_map = {}
            for row in reader:
                cases_map.setdefault(row['laboratory'], []).append(row['case'])
        return cases_map

    def _get_laboratory(self, lab_label):
        try:
            return Laboratory.objects.get(label__iexact=lab_label)
        except Laboratory.DoesNotExist:
            logger.warn('Laboratory %s does not exist' % lab_label)
            return None

    def _get_case(self, case_id):
        try:
            return Case.objects.get(id=case_id)
        except Case.DoesNotExist:
            logger.warn('Case %s does not exist' % case_id)
            return None

    def _update_case(self, case_obj, laboratory_obj):
        case_obj.laboratory = laboratory_obj
        case_obj.save()

    def handle(self, *args, **opts):
        logger.info('=== Starting update job ===')
        cases_map = self._get_cases_map(opts['cases_map'])
        for lab, cases in cases_map.iteritems():
            lab_obj = self._get_laboratory(lab)
            if lab_obj:
                logger.info('Processing cases for laboratory %s', lab)
                for case in cases:
                    case_obj = self._get_case(case)
                    if case_obj:
                        logger.info('Updating case %s' % case)
                        self._update_case(case_obj, lab_obj)
        logger.info('=== Update job completed ===')
