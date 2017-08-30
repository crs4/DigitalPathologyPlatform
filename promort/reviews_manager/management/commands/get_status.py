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
        logger.info('ROIs annotations count: %d', stats_counter['review_comparisons'])
        logger.info('Completed ROIs annotation(s): %d', stats_counter['completed_review_comparisons'])
        logger.info('Unfinished ROIs annotation(s): %d', stats_counter['not_completed_review_comparisons'])
        if stats_counter['not_completed_review_comparisons'] > 0:
            logger.info('--- Stats for each reviewer ---')
            for reviewer, counter in reviewers_counter.iteritems():
                logger.info('Reviewer "%s" still needs to complete %d clinical review(s)', reviewer, counter)
        logger.info('############################')
