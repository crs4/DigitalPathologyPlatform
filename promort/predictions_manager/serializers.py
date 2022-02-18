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

try:
    import simplejson as json
except ImportError:
    import json

from rest_framework import serializers

from predictions_manager.models import Prediction, TissueFragmentsCollection, TissueFragment
from slides_manager.serializers import SlideSerializer


class PredictionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Prediction
        fields = ('id', 'label', 'creation_date', 'slide', 'type', 'omero_id', 'provenance',
                  'review_required')
        read_only_fields = ('id', 'creation_date')

    def validate_provenance(self, value):
        try:
            json.loads(value)
            return value
        except ValueError:
            raise serializers.ValidationError('Not a valid JSON in \'provenance\' field')


class PredictionDetailsSerializer(serializers.ModelSerializer):
    slide = SlideSerializer(many=False, read_only=True)

    class Meta:
        model = Prediction
        fields = ('id', 'label', 'creation_date', 'slide', 'type', 'omero_id', 'provenance', 'review_required')
        read_only_fields = ('id', 'label', 'creation_date', 'slide', 'type', 'omero_id', 'provenance',
                            'review_required')


class TissueFragmentsCollectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = TissueFragmentsCollection
        fields = ('id', 'prediction', 'creation_date')
        read_only_fields = ('id', 'creation_date')


class TissueFragmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = TissueFragment
        fields = ('id', 'collection', 'shape_json', 'creation_date')
        read_only_fields = ('id', 'creation_date')

    def validate_shape_json(self, value):
        try:
            json.loads(value)
            return value
        except ValueError:
            raise serializers.ValidationError('Not a valid JSON in \'shape_json\' field')


class TissueFragmentsCollectionDetailsSerializer(serializers.ModelSerializer):
    fragments = TissueFragmentSerializer(many=True, read_only=True)
    prediction = PredictionSerializer(many=False, read_only=True)

    class Meta:
        model = TissueFragmentsCollection
        fields = ('id', 'prediction', 'creation_date', 'fragments')
        read_only_fields = ('id', 'creation_date')
