try:
    import simplejson as json
except ImportError:
    import json


from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from django.http import Http404
from django.db import IntegrityError


class GenericListView(APIView):
    model = None
    model_serializer = None

    def get(self, request, format=None):
        objs = self.model.objects.all()
        serializer = self.model_serializer(objs, many=True)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = self.model_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class GenericDetailView(APIView):
    model = None
    model_serializer = None

    def get_object(self, pk):
        try:
            return self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        obj = self.get_object(pk)
        serializer = self.model_serializer(obj)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    def delete(self, request, pk, format=None):
        obj = self.get_object(pk)
        try:
            obj.delete()
        except IntegrityError:
            return Response({
                'status':'ERROR',
                'message': 'unable to complete delete operation, there are still references to this object'
            }, status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)
