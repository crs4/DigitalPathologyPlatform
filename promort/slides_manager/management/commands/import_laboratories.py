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

from django.core.management.base import BaseCommand
from slides_manager.models import Laboratory

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    Import laboratories from a text file with one laboratory label per line
    """

    def add_arguments(self, parser):
        parser.add_argument('--labs-list', dest='labs_list', type=str, required=True,
                            help='the file containing the list of the laboratories that will be imported')

    def _get_labs_list(self, labs_file):
        with open(labs_file) as lf:
            return [line.replace('\n', '') for line in lf]

    def _save_lab(self, lab_label):
        _, created = Laboratory.objects.get_or_create(
            label__iexact=lab_label,
            defaults={'label': lab_label}
        )
        if created:
            logger.info('Created Laboratory %s', lab_label)
        else:
            logger.info('Laboratory %s already exists', lab_label)

    def handle(self, *args, **opts):
        logger.info('=== Starting import job ===')
        labs_list = self._get_labs_list(opts['labs_list'])
        for lab in labs_list:
            self._save_lab(lab)
        logger.info('=== Import job completed ===')
