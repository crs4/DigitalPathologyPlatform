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

from django.contrib.auth.models import User

from rest_framework import serializers

from shared_datasets_manager.models import SharedDataset, SharedDatasetItem


class SharedDatasetSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = SharedDataset

        fields = ('id', 'label', 'creation_date', 'author', 'description', 'expiry_date', 'hidden',
                  'items_count')
        read_only_fields = ('id', 'creation_date', 'items_count')
        
    @staticmethod
    def get_items_count(self):
        return self.items.count()


class SharedDatasetItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedDatasetItem

        fields = ('id', 'dataset', 'dataset_index', 'slides_set_a', 'slides_set_a_label', 'slides_set_b',
                  'slides_set_b_label', 'creation_date', 'notes')
        read_only_fields = ('id', 'creation_date')


class SharedDatasetDetailsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    items = SharedDatasetItemSerializer(many=True, read_only=True)

    class Meta:
        model = SharedDataset

        fields = ('id', 'label', 'creation_date', 'author', 'description', 'expiry_date', 'hidden', 'items')
        read_only_fields = ('id', 'creation_date', 'items')
