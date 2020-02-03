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
from questionnaires_manager.models import QuestionsSet

import json
import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    Create a new QuestionsSet object. Questions of the set must be specified as a JSON file.
    Executing this command tool will import only one QuestionsSet at a time.
    """

    def add_arguments(self, parser):
        parser.add_argument('--set-label', dest='set_label', type=str, required=True,
                            help='The label for the questions set (must be unique)')
        parser.add_argument('--questions-json', dest='questions_json', type=str, required=True,
                            help='JSON file containing questions in JSON format')
        parser.add_argument('--author', dest='author', type=str, required=True,
                            help='The username of the user that is creating the questions set')

    def _load_questions(self, questions_file):
        try:
            with open(questions_file) as f:
                qj = json.load(f)
                return qj
        except OSError:
            raise CommandError('File %s does not exist' % questions_file)
        except ValueError:
            raise CommandError('Not a valid JSON file')

    def _load_user(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError('User "%s" is not valid' % username)

    def _import_questions_set(self, set_label, questions, author):
        q_set = QuestionsSet(label=set_label, questions_json=json.dumps(questions),
                             author=self._load_user(author))
        try:
            q_set.save()
        except IntegrityError:
            raise CommandError('Duplicated item for label %s' % set_label)

    def handle(self, *args, **opts):
        logger.info('=== Starting import job ===')
        questions = self._load_questions(opts['questions_json'])
        self._import_questions_set(opts['set_label'], questions, opts['author'])
        logger.info('=== Import job completed ===')
