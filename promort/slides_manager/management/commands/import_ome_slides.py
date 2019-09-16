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
from slides_manager.models import Case, Slide
from promort.settings import OME_SEADRAGON_BASE_URL

from urlparse import urljoin
import requests, re

import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    Import slides from a running OMERO server (with ome_seadragon plugin) to ProMort and create
    related Case and Slide objects
    """

    def _split_slide_name(self, slide_name):
        regex = re.compile(r'[a-zA-Z0-9]+-[0-9]+(_[a-zA-Z][0-9]?)?(\.[a-zA-Z0-9]{2,4})?$')
        if regex.match(slide_name):
            return slide_name.split('-')
        else:
            return None, None

    def _load_ome_images(self):
        url = urljoin(OME_SEADRAGON_BASE_URL, 'get/images/index')
        response = requests.get(url)
        if response.status_code == requests.codes.OK:
            slides = response.json()
            slides_map = dict()
            for s in slides:
                case_id, _ = self._split_slide_name(s['name'])
                logger.debug('Slide %s --- Case ID: %s', s, case_id)
                if case_id:
                    slides_map.setdefault(case_id, []).append(s)
                else:
                    logger.warn('%s is not a valid slide name', s['name'])
            return slides_map
        else:
            logger.error('Unable to load slides from OMERO server')
            raise CommandError('Unable to load slides from OMERO server')

    def _get_slide_mpp(self, slide):
        if slide['img_type'] == 'OMERO_IMG':
            url = urljoin(OME_SEADRAGON_BASE_URL, 'deepzoom/image_mpp/%s.dzi' % slide['omero_id'])
        else:
            url = urljoin(OME_SEADRAGON_BASE_URL, 'mirax/deepzoom/image_mpp/%s.dzi' % slide['name'])
        response = requests.get(url)
        if response.status_code == requests.codes.OK:
            logger.info('Loaded image microns per pixel value')
            return response.json()['image_mpp']
        else:
            logger.warn('Unable to load image microns per pixel value, response code %s', response.status_code)
            return 0

    def _get_or_create_case(self, case_id):
        case, created = Case.objects.get_or_create(id=case_id)
        if created:
            logger.info('Created new Case for ID %s', case_id)
        else:
            logger.info('Retrieved Case for ID %s', case_id)
        return case

    def _get_or_create_slide(self, slide_id, case):
        slide, created = Slide.objects.get_or_create(id=slide_id, case=case)
        if created:
            logger.info('Created new Slide for ID %s', slide_id)
        else:
            logger.info('Retrieved Slide for ID %s', slide_id)
        return slide

    def _update_ome_info(self, slide_obj, omero_id, image_type, image_mpp):
        slide_obj.omero_id = omero_id
        slide_obj.image_type = image_type
        slide_obj.image_microns_per_pixel = image_mpp
        slide_obj.save()
        logger.info('Updated slide object with OMERO infos')

    def handle(self, *args, **opts):
        logger.info('=== Starting import job ===')
        slides_map = self._load_ome_images()
        for case_id, slides in slides_map.iteritems():
            case = self._get_or_create_case(case_id)
            for slide_json in slides:
                slide = self._get_or_create_slide(slide_json['name'], case)
                # this will automatically relink ProMort slides to related OMERO slide (if previously unlinked)
                self._update_ome_info(slide, slide_json['omero_id'], slide_json['img_type'],
                                      self._get_slide_mpp(slide_json))
        logger.info('=== Import job completed ===')
