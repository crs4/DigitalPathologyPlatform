from django.core.management.base import BaseCommand, CommandError

from reviews_manager.models import ROIsAnnotation


class Command(BaseCommand):
    help = 'export the list of the slides related to completed reviews'

    def add_arguments(self, parser):
        parser.add_argument('--output_file', dest='out_file', type=str, required=True,
                            help='the output file for the slides list')

    def _get_slides_list(self, annotation):
        return [step.slide.id for step in annotation.steps.all()]

    def handle(self, *args, **opts):
        completed_slides_list = []
        rois_annotations = ROIsAnnotation.objects.all()
        for annotation in rois_annotations:
            if annotation.clinical_annotations_completed():
                completed_slides_list.extend(self._get_slides_list(annotation))
        with open(opts['out_file'], 'w') as ofile:
            for slide in completed_slides_list:
                ofile.write('%s\n' % slide)
