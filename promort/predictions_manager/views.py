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

from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from view_templates.views import GenericDetailView, GenericListView

from predictions_manager.models import Prediction, TissueFragment, TissueFragmentsCollection
from predictions_manager.serializers import PredictionSerializer, TissueFragmentsCollectionSerializer, \
    TissueFragmentSerializer, TissueFragmentsCollectionDetailsSerializer

import logging
logger = logging.getLogger('promort')


class PredictionList(GenericListView):
    model = Prediction
    model_serializer = PredictionSerializer
    permission_classes = (permissions.IsAuthenticated,)


class PredictionDetail(GenericDetailView):
    model = Prediction
    model_serializer = PredictionSerializer
    permission_classes = (permissions.IsAuthenticated,)
