#  Copyright (c) 2020, CRS4
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
from django.contrib.auth.models import User
from django.db import IntegrityError
from questionnaires_manager.models import QuestionnaireRequest, Questionnaire

from csv import DictReader
import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    
    """

    def add_arguments(self, parser):
        parser.add_argument('--questionnaire-requests', dest='questionnaire_requests', type=str,
                            required=True, help='The CSV containing the questionnaire requests')

    def _load_requests_map(self, qreq_file):
        try:
            with open(qreq_file) as f:
                reader = DictReader(f)
                requests_map = dict()
                for row in reader:
                    requests_map.setdefault(row['reviewer'], []).append(row)
            return requests_map
        except OSError:
            raise CommandError('File %s does not exist' % qreq_file)

    def _create_requests(self, reviewer, requests):
        logger.info('-- Creating %d questionnare requests for user %s', len(requests), reviewer)
        try:
            reviewer_obj = User.objects.get(username=reviewer)
        except User.DoesNotExist:
            logger.error('There is no reviewer with username %s', reviewer)
            return None
        for req in requests:
            if req['label'] is None:
                logger.error('Missing label, skipping row')
                continue
            if req['questionnaire_a'] is None:
                logger.error('Missing mandatody questionnaire_a, skipping row')
                continue
            try:
                q_panel_a_obj = Questionnaire.objects.get(label=req['questionnaire_a'])
            except Questionnaire.DoesNotExist:
                logger.error('There is no Questionnaire object with label %s [Quest_A]', req['questionnaire_a'])
                continue
            req_details = {
                'label': req['label'],
                'questionnaire_panel_a': q_panel_a_obj,
                'reviewer': reviewer_obj
            }
            if not req['questionnaire_b'] is None:
                try:
                    req_details['questionnaire_panel_b'] = Questionnaire.objects.get(label=req['questionnaire_b'])
                except Questionnaire.DoesNotExist:
                    logger.error('There is no Questionnaire object with label %s [Quest_B]', req['questionnaire_b'])
                    continue
            try:
                q_req = QuestionnaireRequest(**req_details)
                q_req.save()
            except IntegrityError:
                logger.error('There is already a QuestionnaireRequest with label %s', req_details['label'])

    def handle(self, *args, **opts):
        logger.info('=== Starting import job ===')
        requests_map = self._load_requests_map(opts['questionnaire_requests'])
        for k, v in requests_map.iteritems():
            self._create_requests(k, v)
        logger.info('=== Import job completed ===')
