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
from reviews_manager.models import ReviewsComparison

from collections import Counter
import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = 'get status of the reviews loaded into the system'

    def handle(self, *args, **opts):
        logger.info('Collecting data....')
        stats_counter = Counter()
        reviewers_counter = Counter()

        reviews_comparisons = ReviewsComparison.objects.all()

        stats_counter['review_comparisons'] = len(reviews_comparisons)

        for rcomp in reviews_comparisons:
            if rcomp.is_completed():
                stats_counter['completed_review_comparisons'] += 1
            else:
                stats_counter['not_completed_review_comparisons'] += 1
                for cl_annotation in (rcomp.review_1, rcomp.review_2):
                    if not cl_annotation.is_completed():
                        reviewers_counter[cl_annotation.clinical_annotation.reviewer.username] += 1
        logger.info('Data collected')
        logger.info('############################')
        logger.info('Slides count: %d', stats_counter['review_comparisons'])
        logger.info('Completed Slide annotation(s): %d', stats_counter['completed_review_comparisons'])
        logger.info('Unfinished Slide annotation(s): %d', stats_counter['not_completed_review_comparisons'])
        if stats_counter['not_completed_review_comparisons'] > 0:
            logger.info('--- Stats for each reviewer ---')
            for reviewer, counter in reviewers_counter.items():
                logger.info('Reviewer "%s" still needs to complete %d clinical review(s)', reviewer, counter)
        logger.info('############################')
