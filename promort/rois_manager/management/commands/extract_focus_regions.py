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

from django.core.management.base import BaseCommand, CommandError
from reviews_manager.models import ROIsAnnotationStep
from promort.settings import OME_SEADRAGON_BASE_URL

from csv import DictWriter
try:
    import simplejson as json
except ImportError:
    import json

import logging, sys, os, requests
from urlparse import urljoin
from shapely.geometry import Polygon

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    Extract focus regions as JSON objects
    """

    def add_arguments(self, parser):
        parser.add_argument('--output_folder', dest='out_folder', type=str, required=True,
                            help='path of the output folder for the extracted JSON objects')
        parser.add_argument('--limit-bounds', dest='limit_bounds', action='store_true',
                            help='extract ROIs considering only the non-empty slide region')

    def _load_rois_annotation_steps(self):
        steps = ROIsAnnotationStep.objects.filter(completion_date__isnull=False)
        return steps

    def _get_slide_bounds(self, slide):
        if slide.image_type == 'OMERO_IMG':
            url = urljoin(OME_SEADRAGON_BASE_URL, 'deepzoom/slide_bounds/%d.dzi' % slide.omero_id)
        elif slide.image_type == 'MIRAX':
            url = urljoin(OME_SEADRAGON_BASE_URL, 'mirax/deepzoom/slide_bounds/%s.dzi' % slide.id)
        else:
            logger.error('Unknown image type %s for slide %s', slide.image_type, slide.id)
            return None
        response = requests.get(url)
        if response.status_code == requests.codes.OK:
            return response.json()
        else:
            logger.error('Error while loading slide bounds %s', slide.id)
            return None

    def _extract_points(self, roi_json, slide_bounds):
        points = list()
        shape = json.loads(roi_json)
        segments = shape['segments']
        if len(segments) > 0:
            for x in segments:
                points.append(
                    (
                        x['point']['x'] + int(slide_bounds['bounds_x']),
                        x['point']['y'] + int(slide_bounds['bounds_y'])
                    )
                )
            return points
        else:
            return None

    def _extract_bounding_box(self, roi_points):
        polygon = Polygon(roi_points)
        bounds = polygon.bounds
        return [(bounds[0], bounds[1]), (bounds[2], bounds[3])]

    def _dump_focus_region(self, focus_region, slide_id, slide_bounds, out_folder):
        file_path = os.path.join(out_folder, 'fr_%d.json' % focus_region.id)
        points = self._extract_points(focus_region.roi_json, slide_bounds)
        if points:
            bbox = self._extract_bounding_box(points)
            with open(file_path, 'w') as ofile:
                json.dump(points, ofile)
            return {
                'slide_id': slide_id,
                'region_id': focus_region.id,
                'region_label': focus_region.label,
                'tissue_status': focus_region.tissue_status,
                'file_name': 'fr_%d.json' % focus_region.id,
                'bbox': bbox
            }
        else:
            return None

    def _dump_details(self, details, out_folder):
        with open(os.path.join(out_folder, 'focus_regions.csv'), 'w') as ofile:
            writer = DictWriter(ofile, ['slide_id', 'region_id', 'region_label', 'bbox', 'tissue_status', 'file_name'])
            writer.writeheader()
            writer.writerows(details)

    def _dump_focus_regions(self, step, out_folder, limit_bounds):
        focus_regions = step.focus_regions
        slide = step.slide
        logger.info('Loading info for slide %s', slide.id)
        if not limit_bounds:
            slide_bounds = self._get_slide_bounds(slide)
        else:
            slide_bounds = {'bounds_x': 0, 'bounds_y': 0}
        if slide_bounds:
            logger.info('Dumping %d focus regions for step %s', len(focus_regions), step.label)
            if len(focus_regions) > 0:
                out_path = os.path.join(out_folder, step.slide.id, step.label)
                try:
                    os.makedirs(out_path)
                except OSError:
                    pass
                focus_regions_details = list()
                for fr in focus_regions:
                    frd = self._dump_focus_region(fr, step.slide.id, slide_bounds, out_path)
                    if frd:
                        focus_regions_details.append(frd)
                self._dump_details(focus_regions_details, out_path)

    def _export_data(self, out_folder, limit_bounds=False):
        steps = self._load_rois_annotation_steps()
        logger.info('Loaded %d ROIs Annotation Steps', len(steps))
        for s in steps:
            self._dump_focus_regions(s, out_folder, limit_bounds)

    def handle(self, *args, **opts):
        logger.info('=== Starting export job ===')
        self._export_data(opts['out_folder'], opts['limit_bounds'])
        logger.info('=== Export completed ===')
