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
from django.db import IntegrityError
from slides_manager.models import Slide, SlidesSet, SlidesSetItem

from csv import DictReader
import itertools
import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    """

    def add_arguments(self, parser):
        parser.add_argument('--slides-sets-map', dest='slides_sets_map', type=str, required=True,
                            help='The CSV file containing the set-slide associations, non existing slides sets will be created')

    def _get_slides_sets_map(self, slides_sets_file):
        try:
            with open(slides_sets_file) as ssf:
                reader = DictReader(ssf)
                sets_map = {}
                for row in reader:
                    sets_map.setdefault(row['slides_set_label'], []).append({
                        'slide_label': row['slide_label'],
                        'set_label': row['set_label']
                    })
            return sets_map
        except OSError:
            raise CommandError('File %s does not exist' % slides_sets_file)

    def _get_or_create_slides_sets(self, sets_labels):
        sets = dict()
        for sl in sets_labels:
            set_obj, _ = SlidesSet.objects.get_or_create(id=sl)
            sets[sl] = set_obj
        return sets

    def _get_slides(self, slides_list):
        slides = dict()
        for s in slides_list:
            try:
                s_obj = Slide.objects.get(id=s)
                slides[s] = s_obj
            except Slide.DoesNotExist:
                logger.warning('There is no slide for ID %s' % s)
        return slides

    def _load_slides_set_item(self, set_obj, slide_obj, set_label, set_index):
        ss_item_obj = SlidesSetItem(slide=slide_obj, slides_set=set_obj, set_label=set_label,
                                    set_index=set_index)
        ss_item_obj.save()

    def _load_sets(self, sets_map, slides_set_objs, slides_objs):
        for set_id, items in sets_map.iteritems():
            for index, set_item in enumerate(items):
                try:
                    self._load_slides_set_item(
                        slides_set_objs[set_id],
                        slides_objs[set_item['slide_label']],
                        set_item['set_label'], index
                    )
                except KeyError:
                    pass
                except IntegrityError:
                    logger.error('Integrity Error for set %s, slide %s, set_label %s and index %d',
                                 set_id, set_item['slide_label'], set_item['set_label'], index)

    def handle(self, *args, **opts):
        logger.info('=== Starting import job ===')
        sets_map = self._get_slides_sets_map(opts['slides_sets_map'])
        sets = self._get_or_create_slides_sets(sets_map.keys())
        slides = self._get_slides(set([x['slide_label'] for x in itertools.chain(*sets_map.values())]))
        self._load_sets(sets_map, sets, slides)
        logger.info('=== Import job completed ===')
