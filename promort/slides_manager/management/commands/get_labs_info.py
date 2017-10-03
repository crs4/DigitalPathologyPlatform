from collections import Counter

from django.core.management.base import BaseCommand
from slides_manager.models import Case

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = 'get infos about registered laboratories'

    def handle(self, *args, **opts):
        logger.info('Collecting data...')
        labs_counter = Counter()

        cases = Case.objects.all()

        for c in cases:
            if c.laboratory:
                labs_counter[c.laboratory.label] += 1
            else:
                labs_counter['NO_LAB'] += 1

        logger.info('Done collecting data')

        logger.info('#########################')
        no_labs = labs_counter.pop('NO_LAB', 0)
        for lab, count in labs_counter.iteritems():
            logger.info('Laboratory %s - %d case(s)', lab, count)
        logger.info('%d case(s)  not assigned to a lab', no_labs)
        logger.info('#########################')
