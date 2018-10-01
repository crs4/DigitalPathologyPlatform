from django.core.management.base import BaseCommand
from slides_manager.models import SlideEvaluation

from csv import DictWriter

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    Export existing SlideEvaluation data to CSV
    """

    def add_arguments(self, parser):
        parser.add_argument('--output_file', dest='output', type=str, required=True,
                            help='path of the output CSV file')

    def _load_data(self):
        slides_evaluations = SlideEvaluation.objects.all()
        return slides_evaluations

    def _export_data(self, data, out_file):
        header = ['case_id', 'slide_id', 'roi_review_step_id', 'staining', 'adequate_slide', 'not_adequacy_reason',
                  'notes', 'reviewer', 'acquisition_date']
        with open(out_file, 'w') as ofile:
            writer = DictWriter(ofile, delimiter=',', fieldnames=header)
            writer.writeheader()
            for evaluation in data:
                writer.writerow(
                    {
                        'case_id': evaluation.slide.case.id,
                        'slide_id': evaluation.slide.id,
                        'roi_review_step_id': evaluation.rois_annotation_step.label,
                        'staining': evaluation.get_staining_text(),
                        'adequate_slide': evaluation.adequate_slide,
                        'not_adequacy_reason': evaluation.get_not_adequacy_reason_text(),
                        'notes': evaluation.notes,
                        'reviewer': evaluation.reviewer.username,
                        'acquisition_date': evaluation.acquisition_date.strftime('%Y-%m-%d %H:%M:%S')
                    }
                )

    def handle(self, *args, **opts):
        logger.info('=== Starting export job ===')
        slide_evaluations = self._load_data()
        self._export_data(slide_evaluations, opts['output'])
        logger.info('=== Data saved to %s ===', opts['output'])
