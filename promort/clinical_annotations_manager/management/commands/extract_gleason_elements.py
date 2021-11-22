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
from reviews_manager.models import ClinicalAnnotationStep
from promort.settings import OME_SEADRAGON_BASE_URL

from csv import DictWriter

import logging, os, requests, json
from urllib.parse import urljoin
from shapely.geometry import Polygon

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    Extract Gleason elements as JSON objects
    """

    def add_arguments(self, parser):
        parser.add_argument('--output_folder', dest='out_folder', type=str, required=True,
                            help='path of the output folder for the extracted JSON objects')
        parser.add_argument('--limit-bounds', dest='limit_bounds', action='store_true',
                            help='extract ROIs considering only the non-empty slide region')

    def _load_clinical_annotation_steps(self):
        steps = ClinicalAnnotationStep.objects.filter(completion_date__isnull=False)
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

    def _dump_gleason_element(self, gleason_element, slide_id, slide_bounds, out_folder):
        file_path = os.path.join(out_folder, 'gl_{0}.json'.format(gleason_element.id))
        points = self._extract_points(gleason_element.json_path, slide_bounds)
        if points:
            bbox = self._extract_bounding_box(points)
            with open(file_path, 'w') as ofile:
                json.dump(points, ofile)
            return {
                'slide_id': slide_id,
                'focus_region_id': gleason_element.focus_region_annotation.focus_region.id,
                'author': gleason_element.focus_region_annotation.author.username,
                'gleason_element_id': gleason_element.id,
                'gleason_type': gleason_element.gleason_type,
                'file_name': 'gl_{0}.json'.format(gleason_element.id),
                'bbox': bbox
            }

    def _dump_details(self, details, out_folder):
        with open(os.path.join(out_folder, 'gleason_elements.csv'), 'w') as ofile:
            writer = DictWriter(ofile, ['slide_id', 'focus_region_id', 'author', 'gleason_element_id', 'gleason_type',
                                        'file_name', 'bbox'])
            writer.writeheader()
            writer.writerows(details)

    def _dump_gleason_elements(self, step, out_folder, limit_bounds):
        slide = step.slide
        logger.info('Loading info for slide %s', slide.id)
        if not limit_bounds:
            slide_bounds = self._get_slide_bounds(slide)
        else:
            slide_bounds = {'bounds_x': 0, 'bounds_y': 0}
        if slide_bounds:
            focus_regions = step.focus_region_annotations.all()
            logger.info('Found %d focus region annotations for step %s', len(focus_regions), step.label)
            out_path = os.path.join(out_folder, slide.id, step.label)
            gleason_elements_details = list()
            for fr in focus_regions:
                gleason_elements = fr.gleason_elements.all()
                for ge in gleason_elements:
                    try:
                        os.makedirs(out_path)
                    except OSError:
                        pass
                    ged = self._dump_gleason_element(ge, slide.id, slide_bounds, out_path)
                    if ged:
                        gleason_elements_details.append(ged)
            if len(gleason_elements_details) > 0:
                self._dump_details(gleason_elements_details, out_path)

    def _export_data(self, out_folder, limit_bounds=False):
        steps = self._load_clinical_annotation_steps()
        logger.info('Loaded %d Clinical Annotation Steps', len(steps))
        for s in steps:
            self._dump_gleason_elements(s, out_folder, limit_bounds)

    def handle(self, *args, **opts):
        logger.info('=== Starting export job ===')
        self._export_data(opts['out_folder'], opts['limit_bounds'])
        logger.info('=== Export completed ===')
