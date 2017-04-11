try:
    import simplejson as json
except ImportError:
    import json

from django.contrib.auth.models import User

from rest_framework import serializers

from rois_manager.models import Slice, Core, FocusRegion
from clinical_annotations_manager.models import SliceAnnotation, CoreAnnotation, \
    FocusRegionAnnotation, Gleason4Element
from rois_manager.serializers import SliceSerializer, CoreSerializer, FocusRegionSerializer


class SliceAnnotationSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        model = SliceAnnotation
        fields = ('id', 'author', 'slice', 'annotation_step', 'creation_date', 'high_grade_pin',
                  'pah', 'chronic_inflammation', 'acute_inflammation', 'periglandular_inflammation',
                  'intraglandular_inflammation', 'stromal_inflammation')
        read_only_fields = ('id', 'creation_date')
        write_only_fields = ('annotation_step',)


class SliceAnnotationDetailsSerializer(SliceAnnotationSerializer):
    slice = SliceSerializer(read_only=True)


class SliceAnnotationInfosSerializer(serializers.ModelSerializer):
    class Meta:
        model = SliceAnnotation
        fields = ('id', 'annotation_step')
        read_only_fields = ('id', 'annotation_step')


class CoreAnnotationSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    gleason_score = serializers.SerializerMethodField()
    gleason_4_percentage = serializers.SerializerMethodField()

    class Meta:
        model = CoreAnnotation
        fields = ('id', 'author', 'core', 'annotation_step', 'creation_date', 'primary_gleason',
                  'secondary_gleason', 'gleason_score', 'gleason_4_percentage', 'gleason_group')
        read_only_fields = ('id', 'creation_date', 'gleason_score', 'gleason_4_percentage')
        write_only_fields = ('annotation_step',)

    @staticmethod
    def get_gleason_score(obj):
        return '%d + %d' % (obj.primary_gleason, obj.secondary_gleason)

    @staticmethod
    def get_gleason_4_percentage(obj):
        return obj.get_gleason_4_percentage()


class CoreAnnotationDetailsSerializer(CoreAnnotationSerializer):
    core = CoreSerializer(read_only=True)


class CoreAnnotationInfosSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoreAnnotation
        fields = ('id', 'annotation_step')
        read_only_fields = ('id', 'annotation_step')


class Gleason4ElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gleason4Element
        fields = ('id', 'focus_region_annotation', 'json_path', 'area', 'cellular_density_helper_json',
                  'cellular_density', 'cells_count')
        write_only_fields = ('focus_region_annotation',)

    @staticmethod
    def validate_json_path(value):
        try:
            json.loads(value)
            return value
        except ValueError:
            raise serializers.ValidationError('Not a valid JSON in \'json_path\' field')

    @staticmethod
    def validate_cellular_density_helper_json(value):
        try:
            json.loads(value)
            return value
        except ValueError:
            raise serializers.ValidationError('Not a valid JSON in \'cellular_density_helper_json\' field')


class FocusRegionAnnotationSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    gleason_4_elements = Gleason4ElementSerializer(many=True)

    class Meta:
        model = FocusRegionAnnotation
        fields = ('id', 'author', 'focus_region', 'annotation_step', 'creation_date', 'perineural_involvement',
                  'intraductal_carcinoma', 'ductal_carcinoma', 'poorly_formed_glands', 'cribriform_pattern',
                  'small_cell_signet_ring', 'hypernephroid_pattern', 'mucinous', 'comedo_necrosis',
                  'gleason_4_elements', 'cellular_density_helper_json', 'cellular_density', 'cells_count')
        read_only_fields = ('id', 'creation_date')
        write_only_fields = ('annotation_step',)


class FocusRegionAnnotationDetailsSerializer(FocusRegionAnnotationSerializer):
    focus_region = FocusRegionSerializer(read_only=True)


class FocusRegionAnnotationInfosSerializer(serializers.ModelSerializer):
    class Meta:
        model = FocusRegionAnnotation
        fields = ('id', 'annotation_step')
        read_only_fields = ('id', 'annotation_step')


class AnnotatedFocusRegionSerializer(serializers.ModelSerializer):
    clinical_annotations = FocusRegionAnnotationInfosSerializer(many=True)

    class Meta:
        model = FocusRegion
        fields = ('id', 'label', 'core', 'roi_json', 'length', 'area',
                  'cancerous_region', 'clinical_annotations')
        read_only_fields = fields


class AnnotatedCoreSerializer(serializers.ModelSerializer):
    focus_regions = AnnotatedFocusRegionSerializer(many=True)
    clinical_annotations = CoreAnnotationInfosSerializer(many=True)
    positive = serializers.SerializerMethodField()

    class Meta:
        model = Core
        fields = ('id', 'label', 'slice', 'roi_json', 'length', 'area', 'tumor_length',
                  'focus_regions', 'clinical_annotations', 'positive')
        read_only_fields = fields

    @staticmethod
    def get_positive(obj):
        for fr in obj.focus_regions.all():
            if fr.cancerous_region:
                return True
        return False


class AnnotatedSliceSerializer(serializers.ModelSerializer):
    cores = AnnotatedCoreSerializer(many=True)
    clinical_annotations = SliceAnnotationInfosSerializer(many=True)

    class Meta:
        model = Slice
        fields = ('id', 'label', 'slide', 'roi_json', 'cores', 'clinical_annotations')
        read_only_fields = fields
