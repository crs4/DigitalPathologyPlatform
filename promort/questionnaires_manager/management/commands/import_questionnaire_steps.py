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
from django.db import IntegrityError
from questionnaires_manager.models import Questionnaire, QuestionnaireStep, QuestionsSet
from slides_manager.models import SlidesSet

from csv import DictReader
from uuid import uuid4
import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    
    """

    def add_arguments(self, parser):
        parser.add_argument('--questionnaire-steps', dest='questionnaire_steps_file', type=str, required=True,
                            help='The CSV file containing the questionnare steps definitions')

    def _load_questionnaires_map(self, qsteps_file):
        try:
            with open(qsteps_file) as f:
                reader = DictReader(f)
                questionnaire_map = dict()
                for row in reader:
                    questionnaire_map.setdefault(row['questionnaire'], []).append(row)
                return questionnaire_map
        except OSError:
            raise CommandError('File %s does not exist' % qsteps_file)

    def _get_slides_set_random_label(self):
        return str(uuid4())

    def _import_questionnaire_steps(self, questionnaire_label, steps):
        logger.info('-- Creating %d steps for Questionnaire %s', len(steps), questionnaire_label)
        try:
            questionnaire_obj = Questionnaire.objects.get(label=questionnaire_label)
            # create random labels to be used for all the steps of the questionnaire if label is not specified in CSV
            step_a_random_label = self._get_slides_set_random_label()
            step_b_random_label = self._get_slides_set_random_label()
            for i, step in enumerate(steps):
                step_config = {
                    'questionnaire': questionnaire_obj,
                    'step_index': i
                }
                logger.debug('Creating step %d for questionnaire %s', i, questionnaire_label)
                try:
                    step_config['questions'] = QuestionsSet.objects.get(label=step['questions_set'])
                except QuestionsSet.DoesNotExist:
                    logger.error('There is no QuestionsSet object with label %s', step['questions_set'])
                    break
                if not step['slides_set_a'] is None:
                    if step['slides_set_a_label'] in (None, ''):
                        logger.info('Using random label %s for slides set A', step_a_random_label)
                        step['slides_set_a_label'] = step_a_random_label
                    try:
                        step_config.update({
                            'slides_set_a': SlidesSet.objects.get(id=step['slides_set_a']),
                            'slides_set_a_label': step['slides_set_a_label']
                        })
                    except SlidesSet.DoesNotExist:
                        logger.error('There is no SlidesSet object with ID %s', step['slides_set_a'])
                        break
                if not step['slides_set_b'] is None:
                    if step['slides_set_b_label'] in (None, ''):
                        logger.info('Using random label %s for slides set B', step_b_random_label)
                        step['slides_set_b_label'] = step_b_random_label
                    try:
                        step_config.update({
                            'slides_set_b': SlidesSet.objects.get(id=step['slides_set_b']),
                            'slides_set_b_label': step['slides_set_b_label']
                        })
                    except SlidesSet.DoesNotExist:
                        logger.error('There is no SlidesSet object with ID %s', step['slides_set_b'])
                        break
                try:
                    qstep = QuestionnaireStep(**step_config)
                    qstep.save()
                    logger.info('Saved questionnaire step with index %d', i)
                except IntegrityError:
                    logger.error('Questionnaire %s already has a step with index %d', questionnaire_label, i)
                    break
        except Questionnaire.DoesNotExist:
            logger.error('There is no Questionnaire object with label %s, skipping records',
                         questionnaire_label)

    def handle(self, *args, **opts):
        logger.info('=== Starting import job ===')
        questionnaires_map = self._load_questionnaires_map(opts['questionnaire_steps_file'])
        for k, v in questionnaires_map.iteritems():
            self._import_questionnaire_steps(k, v)
        logger.info('=== Import job completed ===')
