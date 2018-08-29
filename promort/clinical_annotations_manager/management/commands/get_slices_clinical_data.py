from django.core.management.base import BaseCommand
from clinical_annotations_manager.models import SliceAnnotation

from csv import DictWriter

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    Export existing Slice clinical data to CSV
    """

    def add_arguments(self, parser):
        parser.add_argument('--output_file', dest='output', type=str, required=True,
                            help='path of the output CSV file')

    def _load_data(self):
        slice_annotations = SliceAnnotation.objects.all()
        return slice_annotations

    def _export_data(self, data, out_file):
        header = ['case_id', 'slide_id', 'rois_review_step_id', 'clinical_review_step_id',
                  'reviewer', 'slice_id', 'creation_date', 'high_grade_pin', 'pah', 'chronic_inflammation',
                  'acute_inflammation', 'periglandular_inflammation',
                  'intraglandular_inflammation', 'stromal_inflammation']
        with open(out_file, 'w') as ofile:
            writer = DictWriter(ofile, delimiter=',', fieldnames=header)
            writer.writeheader()
            for slice_annotation in data:
                writer.writerow(
                    {
                        'case_id': slice_annotation.slice.slide.case.id,
                        'slide_id': slice_annotation.slice.slide.id,
                        'rois_review_step_id': slice_annotation.annotation_step.rois_review_step.label,
                        'clinical_review_step_id': slice_annotation.annotation_step.label,
                        'reviewer': slice_annotation.author.username,
                        'slice_id': slice_annotation.slice.id,
                        'creation_date': slice_annotation.creation_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'high_grade_pin': slice_annotation.high_grade_pin,
                        'pah': slice_annotation.pah,
                        'chronic_inflammation': slice_annotation.chronic_inflammation,
                        'acute_inflammation': slice_annotation.acute_inflammation,
                        'periglandular_inflammation': slice_annotation.periglandular_inflammation,
                        'intraglandular_inflammation': slice_annotation.intraglandular_inflammation,
                        'stromal_inflammation': slice_annotation.stromal_inflammation
                    }
                )

    def handle(self, *args, **opts):
        logger.info('=== Starting export job ===')
        slice_annotations = self._load_data()
        self._export_data(slice_annotations, opts['output'])
        logger.info('=== Data saved to %s ===', opts['output'])
