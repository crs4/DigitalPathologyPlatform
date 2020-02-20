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
from questionnaires_manager.models import QuestionnaireRequest

from csv import DictWriter
from json import loads

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help="""
    """

    def add_arguments(self, parser):
        parser.add_argument('--central-reviewer', dest='central_reviewer', type=str, required=True,
                            help='The username of the central reviewer, used to group answers')
        parser.add_argument('--output-file', dest='out_file', type=str, required=True,
                            help='The path of the output CSV file')

    def _load_questionnaire_answers(self):
        answers = dict()
        for req in QuestionnaireRequest.objects.filter(completion_date__isnull=False):
            for x in req.answers.all():
                answers.setdefault(x.questionnaire.label, []).append(x)
        return answers

    def _extract_case_label(self, request_label):
        return '-'.join(request_label.split('-')[0:-1])

    def _build_answers_map(self, answers, reviewer):
        answers_map = dict()
        local_reviewers_map = dict()
        for req_label, q_answers in answers.iteritems():
            label = self._extract_case_label(req_label)
            answers_map.setdefault(label, dict())
            for a in q_answers:
                if a.reviewer.username == reviewer:
                    rev_type = 'central'
                else:
                    rev_type = 'local'
                    local_reviewers_map[label] = a.reviewer.username
                for step in a.steps.all():
                    answers_map[label].setdefault(rev_type, {}).update(loads(step.answers_json))
        logger.debug(answers_map)
        logger.debug(local_reviewers_map)
        return answers_map, local_reviewers_map

    def _dump_data(self, answers_map, reviewers_map, out_file):
        with open(out_file, 'w') as f:
            file_headers = ['local_reviewer', 'case_label', 'question_1', 'question_2', 'question_3', 'VAS_scale',
                            'central_rev_q1', 'central_rev_q2', 'central_rev_q3']
            writer = DictWriter(f, file_headers)
            writer.writeheader()
            for case, answers in answers_map.iteritems():
                # TODO map to proper file structure
                row = {
                    'local_reviewer': reviewers_map[case],
                    'case_label': case,
                    'question_1': answers['local']['q1'],
                    'question_2': answers['local']['q2'],
                    'question_3': answers['local']['q3'],
                    'VAS_scale': answers['local']['slider_test'],
                    'central_rev_q1': answers['central']['q1'],
                    'central_rev_q2': answers['central']['q2'],
                    'central_rev_q3': answers['central']['q3']
                }
                writer.writerow(row)

    def handle(self, *args, **opts):
        logger.info('=== Start data export ===')
        answers = self._load_questionnaire_answers()
        logger.info('Loaded answers for %d completed questionnaires', len(answers))
        answers_map, reviewers_map = self._build_answers_map(answers, opts['central_reviewer'])
        logger.info('Saving to file %s', opts['out_file'])
        self._dump_data(answers_map, reviewers_map, opts['out_file'])
        logger.info('=== Export completed ===')
