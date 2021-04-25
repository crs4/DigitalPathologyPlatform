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
        for lab, count in labs_counter.items():
            logger.info('Laboratory %s - %d case(s)', lab, count)
        logger.info('%d case(s)  not assigned to a lab', no_labs)
        logger.info('#########################')
