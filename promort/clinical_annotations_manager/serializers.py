try:
    import simplejson as json
except ImportError:
    import json

from django.contrib.auth.models import User

from rest_framework import serializers

from clinical_annotations_manager.models import SliceAnnotation, CoreAnnotation, \
    FocusRegionAnnotation


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


class CoreAnnotationSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    gleason_score = serializers.SerializerMethodField()

    class Meta:
        model = CoreAnnotation
        fields = ('id', 'author', 'core', 'annotation_step', 'creation_date', 'primary_gleason',
                  'secondary_gleason', 'gleason_score', 'gleason_4_percentage', 'gleason_group')
        read_only_fields = ('id', 'creation_date', 'gleason_score')
        write_only_fields = ('annotation_step',)

    @staticmethod
    def get_gleason_score(obj):
        return '%d + %d' % (obj.primary_gleason, obj.secondary_gleason)


class FocusRegionAnnotationSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        model = FocusRegionAnnotation
        fields = ('id', 'author', 'focus_region', 'annotation_step', 'creation_date', 'perineural_involvement',
                  'intraductal_carcinoma', 'poorly_formed_glands', 'cribriform_pattern', 'small_cell_signer_ring',
                  'hypernephroid_pattern', 'mucinous', 'comedo_necrosis', 'gleason_4_path_json', 'gleason_4_area',
                  'cellular_density_helper_json', 'cellular_density')
        read_only_fields = ('id', 'creation_date')
        write_only_fields = ('annotation_step',)

    @staticmethod
    def validate_gleason_4_path_json(value):
        try:
            json.loads(value)
            return value
        except ValueError:
            raise serializers.ValidationError('Not a valid JSON in \'gleason_4_path_json\' field')

    @staticmethod
    def validate_cellular_density_helper_json(value):
        try:
            json.loads(value)
            return value
        except ValueError:
            raise serializers.ValidationError('Not a valid JSON in \'cellular_density_helper_json\' field')
