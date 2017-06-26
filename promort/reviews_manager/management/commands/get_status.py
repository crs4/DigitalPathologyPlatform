from django.core.management.base import BaseCommand
from reviews_manager.models import ROIsAnnotation

from collections import Counter
import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = 'get status of the reviews loaded into the system'

    def handle(self, *args, **opts):
        logger.info('Collecting data....')
        stats_counter = Counter()
        reviewers_counter = Counter()

        rois_annotations = ROIsAnnotation.objects.all()

        stats_counter['rois_annotations'] = len(rois_annotations)

        for annotation in rois_annotations:
            if annotation.clinical_annotations_completed():
                stats_counter['completed_annotations'] += 1
            else:
                stats_counter['not_completed_annotations'] += 1
                for cl_annotation in annotation.clinical_annotations.all():
                    if not cl_annotation.is_completed():
                        reviewers_counter[cl_annotation.reviewer.username] += 1
        logger.info('Data collected')
        logger.info('############################')
        logger.info('ROIs annotations count: %d', stats_counter['rois_annotations'])
        logger.info('Completed ROIs annotation(s): %d', stats_counter['completed_annotations'])
        logger.info('Unfinished ROIs annotation(s): %d', stats_counter['not_completed_annotations'])
        if stats_counter['not_completed_annotations'] > 0:
            logger.info('--- Stats for each reviewer ---')
            for reviewer, counter in reviewers_counter.iteritems():
                logger.info('Reviewer "%s" still needs to complete %d clinical review(s)', reviewer, counter)
        logger.info('############################')
