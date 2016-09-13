try:
    import simplejson as json
except ImportError:
    import json

from django.contrib.auth.models import User

from rest_framework import serializers

from rois_manager.models import Slice, Core, CellularFocus
from slides_manager.models import Slide


class SliceSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    cores_count = serializers.SerializerMethodField()

    class Meta:
        model = Slice
        fields = ('id', 'label', 'slide', 'author', 'creation_date', 'roi_json',
                  'total_cores', 'positive_cores', 'cores_count')
        read_only_fields = ('id', 'creation_date', 'cores_count')

    def get_cores_count(self, obj):
        return obj.cores.count()

    def validate_roi_json(self, value):
        try:
            json.loads(value)
            return value
        except ValueError:
            raise serializers.ValidationError('Not a valid JSON in \'roi_json\' field')


class CoreSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    cellular_focuses_count = serializers.SerializerMethodField()

    class Meta:
        model = Core
        fields = ('id', 'label', 'slice', 'author', 'creation_date', 'roi_json',
                  'length', 'area', 'cellular_focuses_count')
        read_only_fields = ('id', 'creation_date', 'cellular_focuses_count')

    def get_cellular_focuses_count(self, obj):
        return obj.cellular_focuses.count()

    def validate_roi_json(self, value):
        try:
            json.loads(value)
            return value
        except ValueError:
            raise serializers.ValidationError('Not a valid JSON in \'roi_json\' field')


class CellularFocusSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        model = CellularFocus
        fields = ('id', 'label', 'core', 'author', 'creation_date', 'roi_json'
                  'length', 'area', 'cancerous_region')
        read_only_fields = ('id', 'creation_date',)

    def validate_roi_json(self, value):
        try:
            json.loads(value)
            return value
        except ValueError:
            raise serializers.ValidationError('Not a valid JSON in \'roi_json\' field')


class CoreDetailsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    cellular_focuses = CellularFocusSerializer(many=True, read_only=True)

    class Meta:
        model = Core
        fields = ('id', 'label', 'slice', 'author', 'creation_date',
                  'roi_json', 'length', 'area', 'cellular_focuses')
        read_only_fields = ('id', 'creation_date')

    def validate_roi_json(self, value):
        try:
            json.loads(value)
        except ValueError:
            raise serializers.ValidationError('Not a valid JSON in \'roi_json\' field')


class SliceDetailsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    cores = CoreSerializer(many=True, read_only=True)

    class Meta:
        model = Slice
        fields = ('id', 'label', 'slide', 'author', 'creation_date',
                  'roi_json', 'total_cores', 'positive_cores', 'cores')
        read_only_fields = ('id', 'creation_date')

    def validate_roi_json(self, value):
        try:
            json.loads(value)
        except ValueError:
            raise serializers.ValidationError('Not a valid JSON in \'roi_json\' field')


class SlideDetailsSerializer(serializers.ModelSerializer):
    quality_control_passed = serializers.SlugRelatedField(
        read_only=True,
        slug_field='adequate_slide'
    )

    slices = SliceSerializer(many=True)

    class Meta:
        model = Slide
        fields = ('id', 'case', 'import_date', 'omero_id', 'image_type',
                  'quality_control_passed', 'image_microns_per_pixel', 'slices')
        read_only_fields = fields
