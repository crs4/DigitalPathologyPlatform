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

from csv import DictReader, DictWriter
from uuid import uuid4
import logging, sys

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from promort.settings import DEFAULT_GROUPS
from predictions_manager.models import Prediction
from reviews_manager.models import PredictionReview

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = 'build Predictions reviews worklist'

    def add_arguments(self, parser):
        parser.add_argument('--prediction-type', choices=['TUMOR', 'GLEASON'], type=str, dest='prediction_type',
                            help='the type of the Prediction objects that are going to be reviewed')
        parser.add_argument('--worklist-file', dest='worklist', type=str, default=None,
                            help='a CSV file containing the worklist, if not present reviews will be assigned randomly')
        parser.add_argument('--allow-duplicated', action='store_true', dest='allow_duplicated',
                            help='create worklist even for predictions that already have a related review')
        parser.add_argument('--report-file', dest='report_file', type=str, default=None,
                            help='a CSV file containing a report of the created prediction reviews')

    def _get_prediction_reviews_manager_users(self):
        prev_manager_group = Group.objects.get(name=DEFAULT_GROUPS['prediction_manager']['name'])
        return prev_manager_group.user_set.all()

    def _get_predictions_list(self, prediction_type):
        return Prediction.objects.filter(type=prediction_type).all()

    def _check_duplicated(self, prediction, reviewer):
        annotation_objs = PredictionReview.objects.filter(prediction=prediction, reviewer=reviewer)
        if annotation_objs.count() > 0:
            logger.info('There are already %d reviews for prediction %s assigned to user %s',
                        annotation_objs.count(), prediction.label, reviewer.username)
            return True
        else:
            return False

    def _create_prediction_annotation(self, prediction, reviewer, allow_duplicated):
        if not allow_duplicated:
            if self._check_duplicated(prediction, reviewer):
                return None
        prev_obj = PredictionReview(
            label=uuid4().hex,
            prediction=prediction,
            slide=prediction.slide,
            reviewer=reviewer
        )
        prev_obj.save()
        return {
            'review_id': prev_obj.id,
            'slide': prev_obj.slide.id,
            'prediction': prev_obj.prediction.label,
            'review_label': prev_obj.label,
            'reviewer': prev_obj.reviewer.username
        }

    def create_random_worklist(self, prediction_type, allow_duplicated, report_file=None):
        logger.info('Creating RANDOM worklist')
        prediction_rev_managers = self._get_prediction_reviews_manager_users()
        if len(prediction_rev_managers) < 1:
            raise CommandError('No prediction managers configured')
        predictions = self._get_predictions_list(prediction_type)
        for i, pred in enumerate(predictions):
            logger.info('Processing prediction %s', pred.label)
            pred_report = self._create_prediction_annotation(pred,
                                                             prediction_rev_managers[i % len(prediction_rev_managers)],
                                                             allow_duplicated)
            if report_file and pred_report:
                report_file.writerow(pred_report)

    def create_worklist_from_file(self, worklist_file, prediction_type, allow_duplicated, report_file=None):
        raise NotImplementedError()

    def handle(self, *args, **opts):
        logger.info('=== Starting Predictions Reviews worklist creation ===')
        worklist_file = opts['worklist']
        allow_duplicated = opts['allow_duplicated']
        if opts['report_file']:
            report_file = open(opts['report_file'], 'w')
            report_writer = DictWriter(report_file,
                                       ['review_id', 'review_label', 'slide', 'prediction', 'reviewer'])
            report_writer.writeheader()
        else:
            report_writer = None
        try:
            if worklist_file:
                self.create_worklist_from_file(worklist_file, opts['prediction_type'], allow_duplicated, report_writer)
            else:
                self.create_random_worklist(opts['prediction_type'], allow_duplicated, report_writer)
        except CommandError as cme:
            logger.error('A problem occurred while building the worklist, exit')
            sys.exit(cme)
        if report_writer:
            report_file.close()
        logger.info('=== Prediction Reviews worklist creation completed ===')
