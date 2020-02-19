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
from questionnaires_manager.models import Questionnaire
from django.contrib.auth.models import User

from csv import DictReader

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    Create questionnaires from a given CSV file
    """

    def add_arguments(self, parser):
        parser.add_argument('--questionnaires', dest='questionnaires_file', type=str, required=True,
                            help='The CSV file containing the questionnaires definitions')
        parser.add_argument('--author', dest='author', type=str, required=True,
                            help='The username of the user that it\'s creating the questionnaires')

    def _load_questionnaires(self, q_file):
        try:
            with open(q_file) as f:
                reader = DictReader(f)
                questionnaires = set()
                for row in reader:
                    questionnaires.add(row['label'])
                return questionnaires
        except OSError:
            raise CommandError('File %s does not exist' % q_file)

    def _load_questionnaires_author(self, author):
        try:
            return User.objects.get(username=author)
        except User.DoesNotExist:
            raise CommandError('Invalid username "%s"', author)

    def _import_questionnaires(self, questionnaires, author):
        logger.info('--- Loading %d questionnaires', len(questionnaires))
        for q in questionnaires:
            try:
                q_obj = Questionnaire(label=q, author=author)
                q_obj.save()
            except IntegrityError:
                logger.warn('A questionnaire with label "%s" already exists, skipping it', q)

    def handle(self, *args, **opts):
        logger.info('=== Starting import job ===')
        author_obj = self._load_questionnaires_author(opts['author'])
        questionnaires = self._load_questionnaires(opts['questionnaires_file'])
        self._import_questionnaires(questionnaires, author_obj)
        logger.info('=== Import job completed ===')
