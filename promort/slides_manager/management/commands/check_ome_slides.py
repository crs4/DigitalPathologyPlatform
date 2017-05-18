from django.core.management.base import BaseCommand, CommandError

import requests
from urlparse import urljoin

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
