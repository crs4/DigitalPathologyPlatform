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

import requests
from urllib.parse import urljoin

from slides_manager.models import Slide
from promort.settings import OME_SEADRAGON_BASE_URL


class Command(BaseCommand):
    help = 'check if OMERO images related to ProMort slides still exist'

    def _check_slide(self, slide_id, ome_image_id, image_type):
        if image_type == 'MIRAX':
            url = urljoin(OME_SEADRAGON_BASE_URL, 'mirax/deepzoom/get/%s_metadata.json' % slide_id)
        else:
            url = urljoin(OME_SEADRAGON_BASE_URL, 'deepzoom/get/%s_metadata.json' % ome_image_id)
        response = requests.get(url)
        if response.json()['tile_sources']:
            return True
        else:
            return False

    def handle(self, *args, **opts):
        try:
            slides = Slide.objects.filter(omero_id__isnull=False)
        except Slide.DoesNotExist:
            raise CommandError('There is no Slide related to an OMERO image')
        for slide in slides.all():
            self.stdout.write('CHECKING SLIDE %s' % slide.id)
            ome_slide_exists = self._check_slide(slide.id, slide.omero_id, slide.image_type)
            if not ome_slide_exists:
                self.stdout.write('[SLIDE %s] There is no slide in OMERO with ID %s' % (slide.id, slide.omero_id))
                slide.omero_id = None
                slide.image_type = None
                slide.save()
