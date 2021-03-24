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
from rois_manager.serializers import SliceSerializer, CoreSerializer, FocusRegionSerializer

import csv, os, copy
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
        parser.add_argument('--rois-list', dest='rois_list', type=str, required=True,
                            help='A file containing the list of ROIs that will be extracted')
        parser.add_argument('--out-folder', dest='out_folder', type=str, required=True,
                            help='The output folder for the extracted data')

    def _load_rois_map(self, rois_file):
        logger.info('Loading data from CSV file')
        with open(rois_file) as f:
            rois_map = dict()
            reader = csv.DictReader(f)
            for row in reader:
                rois_map.setdefault(row['slide_id'], dict()).setdefault(row['roi_type'], set()).add(int(row['roi_id']))
        return rois_map

    def _get_related(self, rois):
        related_rois = copy.copy(rois)
        related_rois.setdefault('slice', set())
        related_rois.setdefault('core', set())
        related_rois.setdefault('focus_region', set())
        # step 1: process slices
        logger.info('Processing %d slices', len(related_rois['slice']))
        for s in related_rois['slice']:
            s_obj = Slice.objects.get(pk=s)
            # get cores related to given slice
            for c_obj in s_obj.cores.all():
                related_rois['core'].add(c_obj.id)
        # step 2: process focus regions
        logger.info('Processing %d focus regions', len(related_rois['focus_region']))
        for fr in related_rois['focus_region']:
            fr_obj = FocusRegion.objects.get(pk=fr)
            # get core related to given focus region
            related_rois['core'].add(fr_obj.core.id)
        # step 3: process cores
        logger.info('Processing %d cores', len(related_rois['core']))
        for c in related_rois['core']:
            c_obj = Core.objects.get(pk=c)
            # get slice related to given core
            related_rois['slice'].add(c_obj.slice.id)
            # get focus regions related to given core
            for fr_obj in c_obj.focus_regions.all():
                related_rois['focus_region'].add(fr_obj.id)
        logger.info('Retrived %d slices, %d cores, %d focus regions',
                    len(related_rois['slice']), len(related_rois['core']),
                    len(related_rois['focus_region']))
        return related_rois

    def _dump_slide_rois(self, slide_id, rois, output_folder):
        logger.info('Dumping ROIs for slide %s', slide_id)
        rois = self._get_related(rois)
        labels_map = {
            'slice': dict(),
            'core': dict()
        }
        to_be_saved = {
            'slice': list(),
            'core': list(),
            'focus_region': list()
        }
        for s in rois['slice']:
            ser_obj = SliceSerializer(Slice.objects.get(pk=s)).data
            labels_map['slice'][ser_obj.get('id')] = ser_obj['label']
            slice_obj = {
                'label': ser_obj['label'],
                'roi_json': ser_obj['roi_json'],
                'total_cores': ser_obj['total_cores']
            }
            to_be_saved['slice'].append(slice_obj)
        for c in rois['core']:
            ser_obj = CoreSerializer(Core.objects.get(pk=c)).data
            labels_map['core'][ser_obj.get('id')] = ser_obj['label']
            core_obj = {
                'label': ser_obj['label'],
                'slice': labels_map['slice'].get(ser_obj['slice']),
                'roi_json': ser_obj['roi_json'],
                'length': ser_obj['length'],
                'area': ser_obj['area'],
                'tumor_length': ser_obj['tumor_length']
            }
            to_be_saved['core'].append(core_obj)
        for fr in rois['focus_region']:
            ser_obj = FocusRegionSerializer(FocusRegion.objects.get(pk=fr)).data
            focus_region_obj = {
                'label': ser_obj['label'],
                'core': labels_map['core'].get(ser_obj['core']),
                'roi_json': ser_obj['roi_json'],
                'length': ser_obj['length'],
                'area': ser_obj['area'],
                'tissue_status': ser_obj['tissue_status']
            }
            to_be_saved['focus_region'].append(focus_region_obj)
        with open(os.path.join(output_folder, '%s.json' % slide_id), 'w') as out_file:
            json.dump(to_be_saved, out_file)

    def _dump_rois(self, rois_map, output_folder):
        logger.debug('Checking if folder %s exists' % output_folder)
        if not os.path.isdir(output_folder):
            raise CommandError('Output folder %s does not exist, exit' % output_folder)
        for slide, rois in rois_map.items():
            self._dump_slide_rois(slide, rois, output_folder)

    def handle(self, *args, **opts):
        logger.info('== Starting job ==')
        rois = self._load_rois_map(opts['rois_list'])
        self._dump_rois(rois, opts['out_folder'])
        logger.info('== Job completed ==')
