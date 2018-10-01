from django.core.management.base import BaseCommand
from reviews_manager.models import ClinicalAnnotationStep

from csv import DictWriter

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    Export existing ClinicalAnnotationStep data to CSV
    """

    def add_arguments(self, parser):
        parser.add_argument('--output_file', dest='output', type=str, required=True,
                            help='path of the output CSV file')

    def _load_data(self):
        annotation_steps = ClinicalAnnotationStep.objects.all()
        return annotation_steps

    def _get_encoded_note(self, step):
        try:
            return step.notes.encode('utf-8').replace('\n', ' ')
        except AttributeError:
            return None

    def _export_data(self, data, out_file):
        header = ['case_id', 'slide_id', 'roi_review_step_id', 'clinical_annotation_step_id',
                  'creation_date', 'start_date', 'completion_date', 'reviewer', 'rejected',
                  'rejection_reason', 'notes']
        with open(out_file, 'w') as ofile:
            writer = DictWriter(ofile, delimiter=',', fieldnames=header)
            writer.writeheader()
            for step in data:
                writer.writerow(
                    {
                        'case_id': step.slide.case.id,
                        'slide_id': step.slide.id,
                        'roi_review_step_id': step.rois_review_step.label,
                        'clinical_annotation_step_id': step.label,
                        'creation_date': step.creation_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'start_date': step.start_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'completion_date': step.completion_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'reviewer': step.clinical_annotation.reviewer.username,
                        'rejected': step.rejected,
                        'rejection_reason': step.get_rejection_reason_text(),
                        'notes': self._get_encoded_note(step)
                    }
                )

    def handle(self, *args, **opts):
        logger.info('=== Starting export job ===')
        annotation_steps = self._load_data()
        self._export_data(annotation_steps, opts['output'])
        logger.info('=== Data saved to %s ===', opts['output'])
