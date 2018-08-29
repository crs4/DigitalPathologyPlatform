from django.core.management.base import BaseCommand
from clinical_annotations_manager.models import CoreAnnotation

from csv import DictWriter

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    Export existing Core clinical data to CSV
    """

    def add_arguments(self, parser):
        parser.add_argument('--output_file', dest='output', type=str, required=True,
                            help='path of the output CSV file')

    def _load_data(self):
        core_annotations = CoreAnnotation.objects.all()
        return core_annotations

    def _export_data(self, data, out_file):
        header = ['case_id', 'slide_id', 'rois_review_step_id', 'clinical_review_step_id',
                  'reviewer', 'core_id', 'creation_date', 'primary_gleason', 'secondary_gleason',
                  'gleason_group_who_16']
        with open(out_file, 'w') as ofile:
            writer = DictWriter(ofile, delimiter=',', fieldnames=header)
            writer.writeheader()
            for core_annotation in data:
                writer.writerow(
                    {
                        'case_id': core_annotation.core.slice.slide.case.id,
                        'slide_id': core_annotation.core.slice.slide.id,
                        'rois_review_step_id': core_annotation.annotation_step.rois_review_step.label,
                        'clinical_review_step_id': core_annotation.annotation_step.label,
                        'reviewer': core_annotation.author.username,
                        'core_id': core_annotation.core.id,
                        'creation_date': core_annotation.creation_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'primary_gleason': core_annotation.primary_gleason,
                        'secondary_gleason': core_annotation.secondary_gleason,
                        'gleason_group_who_16': core_annotation.get_grade_group_text()
                    }
                )

    def handle(self, *args, **opts):
        logger.info('=== Starting export job ===')
        core_annotations = self._load_data()
        self._export_data(core_annotations, opts['output'])
        logger.info('=== Data saved to %s ===', opts['output'])
