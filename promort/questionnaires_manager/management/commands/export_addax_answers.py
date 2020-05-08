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
        parser.add_argument('--extended', dest='extended_output', action='store_true',
                            help='output will be in extended format')
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

    def _prepare_answers(self, step_obj):
        sample_a_label = step_obj.questionnaire_step.slides_set_a.id
        try:
            sample_b_label = step_obj.questionnaire_step.slides_set_b.id
        except AttributeError:
            sample_b_label = None
        answers_json = loads(step_obj.answers_json)
        sat3_local = answers_json.get('sat-loc_3')
        if sat3_local:
            if sat3_local == 'sample_a':
                answers_json['sat-loc_3'] = sample_a_label
            elif sat3_local == 'sample_b':
                answers_json['sat-loc_3'] = sample_b_label
        sat3_central = answers_json.get('sat-cnt_1')
        if sat3_central:
            if sat3_central == 'sample_a':
                answers_json['sat-cnt_1'] = sample_a_label
            elif sat3_central == 'sample_b':
                answers_json['sat-cnt_1'] = sample_b_label
        return answers_json

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
                    answers_map[label].setdefault(rev_type, {}).update(self._prepare_answers(step))
        return answers_map, local_reviewers_map

    def _dump_data(self, answers_map, reviewers_map, extended_output, out_file):
        with open(out_file, 'w') as f:
            file_headers = ['local_reviewer', 'case_label', 'morphology_1', 'morphology_2', 'morphology_3',
                            'diagnostic_1', 'satisfaction_1', 'satisfaction_2', 'morphology_1_cntr',
                            'morphology_2_cntr', 'morphology_3_cntr', 'diagnostic_1_cntr']
            if extended_output:
                file_headers.insert(8, 'satisfaction_3')
                file_headers.append('satisfaction_3_cntr')
            writer = DictWriter(f, file_headers)
            writer.writeheader()
            for case, answers in answers_map.iteritems():
                row = {
                    'local_reviewer': reviewers_map[case],
                    'case_label': case,
                    'morphology_1': answers['local']['morph_1'],
                    'morphology_2': answers['local']['morph_2'],
                    'morphology_3': answers['local']['morph_3'],
                    'diagnostic_1': answers['local']['diag_1'],
                    'satisfaction_1': answers['local'].get('sat-loc_1'),
                    'satisfaction_2': answers['local'].get('sat-loc_2'),
                    'morphology_1_cntr': answers['central']['morph_1'],
                    'morphology_2_cntr': answers['central']['morph_2'],
                    'morphology_3_cntr': answers['central']['morph_3'],
                    'diagnostic_1_cntr': answers['central']['diag_1'],
                }
                if extended_output:
                    row.update({
                        'satisfaction_3': answers['local'].get('sat-loc_3'),
                        'satisfaction_3_cntr': answers['central'].get('sat-cnt_1')
                    })
                writer.writerow(row)

    def handle(self, *args, **opts):
        logger.info('=== Start data export ===')
        answers = self._load_questionnaire_answers()
        logger.info('Loaded answers for %d completed questionnaires', len(answers))
        answers_map, reviewers_map = self._build_answers_map(answers, opts['central_reviewer'])
        logger.info('Saving to file %s', opts['out_file'])
        self._dump_data(answers_map, reviewers_map, opts['extended_output'], opts['out_file'])
        logger.info('=== Export completed ===')
