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
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        logger.debug('Serializing data %r -- Object class %r', request.data,
                     self.model)
        serializer = self.model_serializer(data=request.data)
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


class GenericReadOnlyDetailView(APIView):
    model = None
    model_serializer = None

    def get_object(self, pk):
        logger.debug('Loading object with PK %r -- Object class %r', pk,
                     self.model)
        try:
            return self.model.objects.get(pk__iexact=pk)
        except self.model.DoesNotExist:
            logger.debug('Object not found!')
            raise NotFound('There is no %s with ID %s' % (self.model, pk))

    def get(self, request, pk, format=None):
        obj = self.get_object(pk)
        serializer = self.model_serializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GenericDetailView(GenericReadOnlyDetailView):
    def put(self, request, pk, format=None):
        logger.debug('Updating object with PK %r -- Object class %r', pk,
                     self.model)
        obj = self.get_object(pk)
        serializer = self.model_serializer(obj,
                                           data=request.data,
                                           partial=True)
        return self._generate_put_response(serializer)

    def delete(self, request, pk, format=None):
        logger.debug('Deleting object with PK %r -- Object class %r', pk,
                     self.model)
        obj = self.get_object(pk)
        return self._generate_delete_response(obj)

    def _generate_put_response(self, serializer):
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

    def _generate_delete_response(self, obj):
        try:
            obj.delete()
        except IntegrityError:
            return Response(
                {
                    'status':
                    'ERROR',
                    'message':
                    'unable to complete delete operation, there are still references to this object'
                },
                status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)
