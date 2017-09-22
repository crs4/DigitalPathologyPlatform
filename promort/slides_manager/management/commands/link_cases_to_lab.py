from django.core.management.base import BaseCommand, CommandError
from slides_manager.models import Laboratory, Case

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    """

    def add_arguments(self, parser):
        parser.add_argument('--laboratory', dest='laboratory', type=str, required=True,
                            help='the label of the laboratory that will be associated to given cases')
        parser.add_argument('--cases-list', dest='cases_list', type=str, required=True,
                            help='the file containing the list of the cases')

    def _get_cases_list(self, cases_file):
        with open(cases_file) as cf:
            return [line.replace('\n', '') for line in cf]

    def _get_laboratory(self, lab_label):
        try:
            return Laboratory.objects.get(label__iexact=lab_label)
        except Laboratory.DoesNotExist:
            raise CommandError('Laboratory %s does not exist' % lab_label)

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
        cases = self._get_cases_list(opts['cases_list'])
        laboratory_obj = self._get_laboratory(opts['laboratory'])
        for case in cases:
            case_obj = self._get_case(case)
            if case_obj:
                logger.info('Updating case %s' % case)
                self._update_case(case_obj, laboratory_obj)
        logger.info('=== Update job completed ===')
