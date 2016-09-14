try:
    import simplejson as json
except ImportError:
    import json


from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from django.db import IntegrityError

import logging
logger = logging.getLogger('promort')


class GenericListView(APIView):
    model = None
    model_serializer = None

    def get(self, request, format=None):
        objs = self.model.objects.all()
        serializer = self.model_serializer(objs, many=True)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    def post(self, request, format=None):
        logger.debug('Serializing data %r -- Object class %r', request.data, self.model)
        serializer = self.model_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class GenericReadOnlyDetailView(APIView):
    model = None
    model_serializer = None

    def get_object(self, pk):
        logger.debug('Loading object with PK %r -- Object class %r', pk, self.model)
        try:
            return self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            logger.debug('Object not found!')
            raise NotFound('There is no %s with ID %s' % (self.model, pk))

    def get(self, request, pk, format=None):
        obj = self.get_object(pk)
        serializer = self.model_serializer(obj)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)


class GenericDetailView(GenericReadOnlyDetailView):

    def delete(self, request, pk, format=None):
        logger.debug('Deleting object with PK %r -- Object class %r', pk, self.model)
        obj = self.get_object(pk)
        try:
            obj.delete()
        except IntegrityError:
            return Response({
                'status': 'ERROR',
                'message': 'unable to complete delete operation, there are still references to this object'
            }, status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)
