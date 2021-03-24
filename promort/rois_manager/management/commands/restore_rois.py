#  Copyright (c) 2020, CRS4
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

from django.core.management.base import BaseCommand, CommandError
from rois_manager.models import Slice, Core, FocusRegion
from slides_manager.models import Slide
from django.contrib.auth.models import User


import glob
try:
    import simplejson as json
except ImportError:
    import json

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    """

    def add_arguments(self, parser):
        parser.add_argument('--rois-folder', dest='rois_folder', type=str, required=True,
                            help='The folder containing ROIs backup as JSON files')
        parser.add_argument('--steps-filter', dest='steps_filter', type=str,
                            help='A text file containing the list of ROIs annotation steps that will be used to restore ROIs')
        parser.add_argument('--author', dest='author', type=str, required=True,
                            help='user that will create the new ROIs')

    def _load_user(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            logger.error('There is no user with username %s', username)
            raise CommandError('There is no user with username %s' % username)

    def _load_rois_map(self, rois_folder):
        roi_files = glob.glob('%s/*.json' % rois_folder)
        logger.info('Found %d JSON files', len(roi_files))
        rois_map = dict()
        for f in roi_files:
            with open(f) as rf:
                rois_map[f.split('/')[-1].replace('.json', '')] = json.load(rf)
        return rois_map

    def _get_steps(self, slides, steps_filter_file):
        steps_map = dict()
        if steps_filter_file:
            with open(steps_filter_file) as f:
                steps_filter = [r.replace('\n', '') for r in f]
        else:
            steps_filter = None
        for s in slides:
            slide_obj = Slide.objects.get(pk=s)
            if steps_filter:
                steps_map[s] = [rs for rs in slide_obj.roi_annotations.all() if rs.label in steps_filter]
            else:
                steps_map[s] = slide_obj.roi_annotations.all()
        logger.debug('Loaded %d ROIs annotation steps', len(steps_map))
        return steps_map

    def _restore_rois(self, rois_map, steps_map, author):
        for slide, rois in rois_map.items():
            logger.info('Processing slide %s', slide)
            steps = steps_map[slide]
            if steps:
                slide_obj = Slide.objects.get(pk=slide)
                slices_map = dict()
                for slice in rois['slice']:
                    for step in steps:
                        logger.debug('Adding slice to step %s', step.label)
                        slice_obj = Slice(slide=slide_obj, annotation_step=step, author=author, **slice)
                        slice_obj.save()
                        slices_map[slice_obj.label] = slice_obj
                cores_map = dict()
                for core in rois['core']:
                    for step in steps:
                        logger.debug('Adding core to step %s', step.label)
                        core_slice = slices_map[core.pop('slice')]
                        core_obj = Core(slice=core_slice, author=author, **core)
                        core_obj.save()
                        cores_map[core_obj.label] = core_obj
                for focus_region in rois['focus_region']:
                    for step in steps:
                        logger.debug('Adding focus region to step %s', step.label)
                        focus_region_core = cores_map[focus_region.pop('core')]
                        focus_region_obj = FocusRegion(core=focus_region_core, author=author, **focus_region)
                        focus_region_obj.save()
            else:
                logger.info('Slide %s has no steps to be processed', slide)

    def handle(self, *args, **opts):
        logger.info('== Starting job ==')
        author = self._load_user(opts['author'])
        rois_map = self._load_rois_map(opts['rois_folder'])
        steps_map = self._get_steps(rois_map.keys(), opts['steps_filter'])
        self._restore_rois(rois_map, steps_map, author)
        logger.info('== Job completed ==')
