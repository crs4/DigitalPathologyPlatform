#  Copyright (c) 2021, CRS4
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

import random
import logging
import operator
from csv import DictWriter
from itertools import izip
from collections import OrderedDict

from slides_manager.models import SlideEvaluation


logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = 'export reviews steps completion times'

    def add_arguments(self, parser):
        parser.add_argument('--out-file', dest='out_file', type=str, required=True,
                            help='output file path')
        parser.add_argument('--hide-slide-id', action='store_true', dest='hide_slide_id',
                            help='replace Slid ID with a random number')

    def _prepare_output_writer(self, out_file):
        f = open(out_file, 'w')
        writer = DictWriter(f, ['slide_id', 'review_index', 'rois_annotation_step', 'rois_start_date', 'rois_completion_date', 'rois_total_time', 'rois_activity_time',
                                'clinical_annotation_step', 'clinical_start_date', 'clinical_completion_date', 'clinical_total_time', 'clinical_activity_time'])
        writer.writeheader()
        return f, writer

    def _get_rois_annotation_steps(self):
        slide_evaluations = SlideEvaluation.objects.filter(adequate_slide=True)
        return [x.rois_annotation_step for x in slide_evaluations]

    def _get_reviews_index(self, rois_annotation_steps):
        reviews_stime = dict()
        for r in rois_annotation_steps:
            reviews_stime.setdefault(r.slide.id, dict())
            reviews_stime[r.slide.id][r.label] = r.start_date
        reviews_index = dict()
        for _, revs in reviews_stime.iteritems():
            sorted_revs = OrderedDict(sorted(revs.items(), key=operator.itemgetter(1)))
            for i, k in enumerate(sorted_revs.keys()):
                reviews_index[k] = i+1
        return reviews_index

    def _get_random_slide_ids(self, slides_list):
        ids = random.sample(xrange(1, 10000000), len(slides_list))
        return dict(izip(slides_list, ids))

    def _get_rois_annotation_step_times(self, step):
        total_time = (step.completion_date - step.start_date).total_seconds()
        activity_time = 0
        for s in step.slices.all():
            if s.creation_start_date:
                activity_time += (s.creation_date - s.creation_start_date).total_seconds()
        for c in step.cores:
            if c.creation_start_date:
                activity_time += (c.creation_date - c.creation_start_date).total_seconds()
        for fr in step.focus_regions:
            if fr.creation_start_date:
                activity_time += (fr.creation_date - fr.creation_start_date).total_seconds()
        return {
            'rois_total_time': total_time,
            'rois_activity_time': activity_time
        }

    def _get_clinical_annotation_step_times(self, step):
        total_time = (step.completion_date - step.start_date).total_seconds()
        activity_time = 0
        for s in step.slice_annotations.all():
            if s.creation_start_date:
                activity_time += (s.creation_date - s.creation_start_date).total_seconds()
        for c in step.core_annotations.all():
            if c.creation_start_date:
                activity_time += (c.creation_date - c.creation_start_date).total_seconds()
        for fr in step.focus_region_annotations.all():
            if fr.creation_start_date:
                activity_time += (fr.creation_date - fr.creation_start_date).total_seconds()
        return {
            'clinical_total_time': total_time,
            'clinical_activity_time': activity_time
        }

    def handle(self, *args, **opts):
        ofp, of_writer = self._prepare_output_writer(opts['out_file'])
        ra_steps = self._get_rois_annotation_steps()
        ra_rev_index = self._get_reviews_index(ra_steps)
        if opts['hide_slide_id']:
            slide_ids_map = self._get_random_slide_ids(set([s.slide.id for s in ra_steps]))
        else:
            slide_ids_map = None
        for rstep in ra_steps:
            if slide_ids_map is not None:
                slide_id = "{:08d}".format(slide_ids_map[rstep.slide.id])
            else:
                slide_id = rstep.slide.id
            rstep_times = self._get_rois_annotation_step_times(rstep)
            for cstep in rstep.clinical_annotation_steps.all():
                row_data = {
                    'slide_id': slide_id,
                    'review_index': ra_rev_index[rstep.label],
                    'rois_annotation_step': rstep.label,
                    'rois_start_date': rstep.start_date,
                    'rois_completion_date': rstep.completion_date,
                }
                if not cstep.rejected:
                    cstep_times = self._get_clinical_annotation_step_times(cstep)
                    row_data.update({
                        'clinical_annotation_step': cstep.label,
                        'clinical_start_date': cstep.start_date,
                        'clinical_completion_date': cstep.completion_date
                    })
                    row_data.update(cstep_times)
                row_data.update(rstep_times)
                of_writer.writerow(row_data)
        ofp.close()
