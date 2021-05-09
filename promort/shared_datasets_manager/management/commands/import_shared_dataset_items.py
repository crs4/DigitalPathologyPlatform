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

from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from shared_datasets_manager.models import SharedDataset, SharedDatasetItem
from slides_manager.models import SlidesSet

from csv import DictReader
import logging

logger = logging.getLogger('promort_commands')


class Command(BaseCommand):
    help = """
    TODO: add doc
    CSV HEADER STRUCTURE
    shared_dataset  slides_set_a    slides_set_a_label  slides_set_b    slides_set_b_label  notes
    """
    
    def add_arguments(self, parser):
        parser.add_argument('--dataset-items', dest='dataset_items_file', type=str, required=True,
                            help='the CSV file containing the shared dataset items definitions')
        
    def _load_datasets_map(self, ditems_file):
        try:
            with open(ditems_file) as f:
                reader = DictReader(f)
                datasets_map = dict()
                for row in reader:
                    datasets_map.setdefault(row['shared_dataset'], list()).append(row)
                return datasets_map
        except OSError:
            raise CommandError('File {0} does not exist'.format(ditems_file))
        
    def _import_shared_dataset_items(self, dataset_label, items):
        logger.info('-- Creating {0} items for dataset {1}'.format(len(items), dataset_label))
        try:
            dataset_obj = SharedDataset.objects.get(label=dataset_label)
            for i in items:
                dset_item_config = {
                    'dataset': dataset_obj
                }
                try:
                    dset_item_config['slides_set_a'] = SlidesSet.objects.get(id=i['slides_set_a'])
                    dset_item_config['slides_set_a_label'] = i['slides_set_a_label']
                except KeyError:
                    logger.error('Missing mandatory field for slides set a')
                    break
                except SlidesSet.DoesNotExist:
                    logger.error('There is no SlidesSet object with label {0}', i['slides_set_a'])
                    break
                if i.get('slides_set_b'):
                    try:
                        dset_item_config['slides_set_b'] = SlidesSet.objects.get(id=i['slides_set_b'])
                        dset_item_config['slides_set_b_label'] = i['slides_set_b_label']
                    except KeyError:
                        logger.error('Missing mandatory field for slides set b')
                        break
                    except SlidesSet.DoesNotExist:
                        logger.error('There is no SlidesSet object with label {0}', i['slides_set_b'])
                        break
                dset_item_config['notes'] = i.get('notes')
                dset_item_obj = SharedDatasetItem(**dset_item_config)
                try:
                    dset_item_obj.save()
                except IntegrityError as ie:
                    logger.error(ie)
                    break
        except SharedDataset.DoesNotExist:
            logger.error('There is no shared dataset object with label {0}, skipping records'.format(dataset_label))

    def handle(self, *args, **opts):
        logger.info('== Starting import job ==')
        shared_datasets_map = self._load_datasets_map(opts['dataset_items_file'])
        for dataset, items in shared_datasets_map.items():
            self._import_shared_dataset_items(dataset, items)
        logger.info('== Import job completed ==')
