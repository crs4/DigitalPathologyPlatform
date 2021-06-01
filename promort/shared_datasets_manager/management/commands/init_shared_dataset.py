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
from django.contrib.auth.models import User
from django.db import IntegrityError
from shared_datasets_manager.models import SharedDataset

from datetime import date
import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    Initialize a new Shared Dataset with given label and author's username. An optional description and an
    expiry date can be specified as well.
    """

    def add_arguments(self, parser):
        parser.add_argument('--label', dest='label', type=str, required=True,
                            help='The label for the new shared dataset')
        parser.add_argument('--author', dest='author', type=str, required=True,
                            help='The username of the user that is creating the questions set')
        parser.add_argument('--description', dest='description', type=str,
                            help='a description for the shared dataset')
        parser.add_argument('--expiry-date', dest='expiry_date', type=date.fromisoformat,
                            help='an expiry date for the shared dataset, format must be YYYY-MM-DD')
        
    def _load_user(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError('User "%s" is not valid' % username)

    def _create_shared_dataset(self, label, author, description=None, expiry_date=None):
        shared_dataset = SharedDataset(label=label, author=self._load_user(author), description=description,
                                       expiry_date=expiry_date)
        try:
            shared_dataset.save()
        except IntegrityError:
            raise CommandError('A SharedDataset with label "{0}" already exists'.format(label))
        
    def handle(self, *args, **opts):
        label = opts['label']
        logger.info('## Creating new shared dataset with label {0}'.format(label))
        self._create_shared_dataset(label, opts['author'], opts['description'], opts['expiry_date'])
        logger.info('## Shared dataset created')
