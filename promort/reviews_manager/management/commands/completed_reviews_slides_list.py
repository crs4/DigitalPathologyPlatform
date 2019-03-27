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

from reviews_manager.models import ClinicalAnnotation, ReviewsComparison

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = 'export the list of the slides related to completed reviews'

    def add_arguments(self, parser):
        parser.add_argument('--output_file', dest='out_file', type=str, required=True,
                            help='the output file for the slides list')
        parser.add_argument('--by_reviews_comparison', dest='by_reviews_comparison', action='store_true',
                            help='use ReviewsComparison objects to decide if the review for a slide is completed, otherwise simply use ClinicalAnnotation')
        parser.add_argument('--linked_only', action='store_true',
                            help='write in the output file only slides linked to images on the OMERO server')

    def _get_slides_by_clinical_annotations(self, ome_link_active):
        completed_slides_list = set()
        clinical_annotations = ClinicalAnnotation.objects.all()
        logger.info('Loaded %d ClinicalAnnotation objects', len(clinical_annotations))
        for ca in clinical_annotations:
            if ca.is_completed():
                slides = self._get_clinical_annotation_slides(ca, ome_link_active)
                completed_slides_list = completed_slides_list.union(slides)
        logger.info('Found %s slides related to completed reviews', len(completed_slides_list))
        return completed_slides_list

    def _get_clinical_annotation_slides(self, clinical_annotation, ome_link_active):
        slides = set()
        for step in clinical_annotation.steps.all():
            if ome_link_active:
                if step.slide.omero_id is not None:
                    slides.add(step.slide.id)
            else:
                slides.add(step.slide.id)
        return slides

    def _get_slides_by_review_comparisons(self, ome_link_active):
        completed_slides_list = set()
        review_comparisons = ReviewsComparison.objects.all()
        logger.info('Loaded %d ReviewsComparison objects', len(review_comparisons))
        for rc in review_comparisons:
            if rc.is_completed() and not rc.is_evaluation_pending():
                s = self._get_slide_by_reviews_comparison(rc, ome_link_active)
                if s is not None:
                    completed_slides_list.add(s)
        logger.info('Found %s slides related to completed reviews', len(completed_slides_list))
        return completed_slides_list

    def _get_slide_by_reviews_comparison(self, reviews_comparison, ome_link_active):
        # check if all related ClinicalAnnotation objects were closed
        if not reviews_comparison.linked_reviews_completed():
            return None
        # review_1 and review_2 point to the same rois_review_step so it is safe to use review_1's
        # slide field to extract the ID
        slide = reviews_comparison.review_1.slide
        if ome_link_active:
            if slide.omero_id is not None:
                return slide.id
            else:
                return None
        else:
            return slide.id

    def _write_output_file(self, completed_slides_list, output_file):
        logger.info('Writing output file')
        with open(output_file, 'w') as ofile:
            for slide in completed_slides_list:
                ofile.write('%s\n' % slide)

    def handle(self, *args, **opts):
        logger.info('=== Exporting list of slides with a complete review workflow ===')
        if opts['by_reviews_comparison']:
            completed_slides_list = self._get_slides_by_review_comparisons(opts['linked_only'])
        else:
            completed_slides_list = self._get_slides_by_clinical_annotations(opts['linked_only'])
        self._write_output_file(completed_slides_list, opts['out_file'])
        logger.info('=== Job completed ===')
