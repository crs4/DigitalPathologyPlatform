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

from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import MethodNotAllowed, NotFound

from view_templates.views import GenericListView, GenericReadOnlyDetailView

from shared_datasets_manager.models import SharedDataset, SharedDatasetItem
from shared_datasets_manager.serializers import SharedDatasetSerializer, SharedDatasetDetailsSerializer,\
    SharedDatasetItemDetailsSerializer

import logging
logger = logging.getLogger('promort')


class SharedDatasetList(GenericListView):
    model = SharedDataset
    model_serializer = SharedDatasetSerializer

    def post(self, request, format=None):
        raise MethodNotAllowed


class SharedDatasetDetail(GenericReadOnlyDetailView):
    model = SharedDataset
    model_serializer = SharedDatasetDetailsSerializer


class SharedDatasetItemDetail(APIView):
    models = SharedDatasetItem
    model_serializer = SharedDatasetItemDetailsSerializer

    def get_object(self, dataset_id, item_index):
        try:
            dset_obj = SharedDataset.objects.get(pk=dataset_id)
            return dset_obj.items.get(dataset_index=item_index)
        except SharedDataset.DoesNotExist:
            raise NotFound('There is no SharedDataset object with ID %s' % dataset_id)
        except SharedDatasetItem.DoesNotExist:
            raise NotFound('There is not item with index %s for SharedDataset %s' % (item_index, dataset_id))

    def get(self, request, dataset, index, format=None):
        dataset_item = self.get_object(dataset, index)
        serializer = self.model_serializer(dataset_item)
        return Response(serializer.data, status=status.HTTP_200_OK)
