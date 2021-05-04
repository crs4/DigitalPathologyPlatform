#  Copyright (c) 2021, CRS4
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

from django.core.management.base import BaseCommand, CommandError
from questionnaires_manager.models import QuestionnaireRequest

from collections import Counter

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
        Extract a report for the QuestionnaireRequest objects on the system and print it as output
        on the terminal
    """

    def _load_questionnaire_requests_map(self):
        qreqs_map = dict()
        for q in QuestionnaireRequest.objects.all():
            qreqs_map.setdefault(q.reviewer.username, list()).append(q)
        return qreqs_map

    def _build_report(self, questionnaire_requests):
        status = Counter()
        for q in questionnaire_requests:
            if q.is_completed():
                status['completed'] += 1
            else:
                if q.is_started():
                    status['on_going'] += 1
                else:
                    status['pending'] += 1
        return status

    def _print_report(self, user, status_report):
        print('==== User: {0} ===='.format(user))
        for x in ['completed', 'on_going', 'pending']:
            try:
                print('* {0} tasks: {1}'.format(x, status_report[x]))
            except KeyError:
                print('* {0} tasks: 0'.format(x))
        print('\n')

    def handle(self, *args, **opts):
        logger.info('--- Building report ---\n')
        qreq_map = self._load_questionnaire_requests_map()
        for user, qreqs in qreq_map.iteritems():
            report = self._build_report(qreqs)
            self._print_report(user, report)
