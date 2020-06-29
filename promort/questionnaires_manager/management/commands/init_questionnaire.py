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
from questionnaires_manager.models import Questionnaire

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    Initialize a Questionnaire object with the given label and author's username.
    """

    def add_arguments(self, parser):
        parser.add_argument('--label', dest='label', type=str, required=True,
                            help='The label for the questionnaire')
        parser.add_argument('--author', dest='author', type=str, required=True,
                            help='The username of the user that is creating the questions set')

    def _load_user(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError('User "%s" is not valid' % username)

    def _create_questionnaire(self, label, author):
        questionnaire = Questionnaire(label=label, author=self._load_user(author))
        try:
            questionnaire.save()
        except IntegrityError:
            raise CommandError('A questionnaire with label "%s" already exist' % label)

    def handle(self, *args, **opts):
        label = opts['label']
        logger.info('## Creating questionnaire with label %s', label)
        self._create_questionnaire(label, opts['author'])
        logger.info('## Questionnaire created')
