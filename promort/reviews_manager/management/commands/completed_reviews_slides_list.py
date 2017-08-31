from django.core.management.base import BaseCommand, CommandError

from reviews_manager.models import ReviewsComparison


class Command(BaseCommand):
    help = 'export the list of the slides related to completed reviews'

    def add_arguments(self, parser):
        parser.add_argument('--output_file', dest='out_file', type=str, required=True,
                            help='the output file for the slides list')

    def _get_slides_list(self, reviews_comparison):
        # review_1 and review_2 point to the same rois_review_step so it is safe to use review_1's
        # slide field to extract the ID
        return reviews_comparison.review_1.slide.id

    def handle(self, *args, **opts):
        completed_slides_list = []
        review_comparions = ReviewsComparison.objects.all()
        for rc in review_comparions:
            if rc.is_completed():
                completed_slides_list.extend(self._get_slides_list(rc))
        with open(opts['out_file'], 'w') as ofile:
            for slide in completed_slides_list:
                ofile.write('%s\n' % slide)
