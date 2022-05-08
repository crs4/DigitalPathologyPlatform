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

import json
import logging

from distutils.util import strtobool

from predictions_manager.models import (Prediction, TissueFragment,
                                        TissueFragmentsCollection)
from predictions_manager.serializers import (
    PredictionSerializer, TissueFragmentsCollectionDetailsSerializer,
    TissueFragmentsCollectionSerializer, TissueFragmentSerializer)
from rest_framework import permissions, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView
from view_templates.views import GenericDetailView, GenericListView

logger = logging.getLogger('promort')


class PredictionList(GenericListView):
    model = Prediction
    model_serializer = PredictionSerializer
    permission_classes = (permissions.IsAuthenticated, )


class PredictionDetail(GenericDetailView):
    model = Prediction
    model_serializer = PredictionSerializer
    permission_classes = (permissions.IsAuthenticated, )


class PredictionDetailBySlide(APIView):
    model_serializer = PredictionSerializer
    permission_classes = (permissions.IsAuthenticated, )
    
    def _find_predictions_by_slide_id(self, slide_id, type=None, fetch_latest=False):
        if type is None:
            predictions = Prediction.objects.filter(slide__id=slide_id)
        else:
            predictions = Prediction.objects.filter(slide__id=slide_id, type=type)
        if fetch_latest:
            return predictions.order_by('-creation_date').first()
        return predictions.all()
        
    
    def get(self, request, pk, format=None):
        fetch_latest = strtobool(request.GET.get('latest', 'false'))
        prediction_type = request.GET.get('type')
        predictions = self._find_predictions_by_slide_id(pk, prediction_type, fetch_latest)
        if (fetch_latest and predictions is None) or (not fetch_latest and len(predictions) == 0):
            raise NotFound(f'No predictions found for the required query')
        else:
            serializer = self.model_serializer(predictions, many = not fetch_latest)
            return Response(serializer.data, status=status.HTTP_200_OK)


class PredictionRequireReview(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    
    def _find_prediction(self, label):
        try:
            prediction = Prediction.objects.get(label=label)
            return prediction
        except Prediction.DoesNotExist:
            raise NotFound(f'No prediction review item with label \'{label}\'')
    
    def put(self, request, label, format=None):
        prediction = self._find_prediction(label)
        prediction.require_review()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TissueFragmentsCollectionList(GenericListView):
    model = TissueFragmentsCollection
    model_serializer = TissueFragmentsCollectionSerializer
    permission_classes = (permissions.IsAuthenticated, )


class TissueFragmentsCollectionDetail(GenericDetailView):
    model = TissueFragmentsCollection
    model_serializer = TissueFragmentsCollectionSerializer
    permission_classes = (permissions.IsAuthenticated, )


class TissueFragmentList(APIView):
    model_serializer = TissueFragmentSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, coll_id, format=None):
        collection = TissueFragmentsCollection.objects.get(pk=coll_id)
        objs = collection.fragments.all()
        serializer = self.model_serializer(objs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, coll_id, format=None):
        logger.info('post TissueFragmentList with data %s and coll_id %s',
                    request.data, coll_id)
        data = request.data
        data['shape_json'] = json.dumps(data['shape_json'])
        data['collection'] = coll_id
        serializer = self.model_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            for errors in serializer.errors.values():
                for err in errors:
                    if err.code == 'unique':
                        return Response(serializer.errors,
                                        status=status.HTTP_409_CONFLICT)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class TissueFragmentsDetail(GenericDetailView):
    model = TissueFragment
    model_serializer = TissueFragmentSerializer

    def get(self, request, coll_id, pk, format=None):
        obj = self.get_object(pk)
        self._check_collection(obj, coll_id)
        serializer = self.model_serializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, coll_id, pk, format=None):
        obj = self.get_object(pk)
        self._check_collection(obj, coll_id)
        serializer = self.model_serializer(obj,
                                           data=request.data,
                                           partial=True)
        return self._generate_put_response(serializer)

    def delete(self, request, coll_id, pk, format=None):
        logger.debug('Deleting object with PK %r -- Object class %r', pk,
                     self.model)
        obj = self.get_object(pk)
        self._check_collection(obj, coll_id)
        return self._generate_delete_response(obj)

    def _check_collection(self, obj, coll_id):
        if obj.collection.pk != int(coll_id):
            raise TissueFragmentNotInCollection(
                f'tissue fragment {obj.pk} is in collection {obj.collection.pk}, not in {coll_id}'
            )


class TissueFragmentNotInCollection(Exception):
    ...
