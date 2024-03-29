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

try:
    import simplejson as json
except ImportError:
    import json

from django.contrib.auth.models import User

from rest_framework import serializers

from rois_manager.models import Slice, Core, FocusRegion
from clinical_annotations_manager.models import SliceAnnotation, CoreAnnotation, \
    FocusRegionAnnotation, GleasonPattern, GleasonPatternSubregion
from rois_manager.serializers import SliceSerializer, CoreSerializer, FocusRegionSerializer


class SliceAnnotationSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    gleason_4_percentage = serializers.SerializerMethodField()

    class Meta:
        model = SliceAnnotation
        fields = ('id', 'author', 'slice', 'annotation_step', 'action_start_time', 'action_complete_time', 
                  'creation_date', 'high_grade_pin', 'pah', 'chronic_inflammation', 'acute_inflammation',
                  'periglandular_inflammation', 'intraglandular_inflammation', 'stromal_inflammation',
                  'gleason_4_percentage')
        read_only_fields = ('id', 'creation_date', 'gleason_4_percentage')
        write_only_fields = ('annotation_step',)

    @staticmethod
    def get_gleason_4_percentage(obj):
        return obj.get_gleason_4_percentage()


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
    largest_confluent_sheet = serializers.SerializerMethodField()
    total_cribriform_area = serializers.SerializerMethodField()

    class Meta:
        model = CoreAnnotation
        fields = ('id', 'author', 'core', 'annotation_step', 'action_start_time', 'action_complete_time',
                  'creation_date', 'gleason_score', 'gleason_4_percentage', 'nuclear_grade_size',
                  'intraluminal_acinar_differentiation_grade', 'intraluminal_secretions',
                  'central_maturation', 'extra_cribriform_gleason_score',
                  'largest_confluent_sheet', 'total_cribriform_area', 'predominant_rsg',
                  'highest_rsg', 'rsg_within_highest_grade_area', 'rsg_in_area_of_cribriform_morphology',
                  'perineural_invasion', 'perineural_growth_with_cribriform_patterns',
                  'extraprostatic_extension')
        read_only_fields = ('id', 'creation_date', 'gleason_score', 'gleason_4_percentage', 'largest_confluent_sheet',
                            'total_cribriform_area')
        write_only_fields = ('annotation_step',)

    @staticmethod
    def get_gleason_score(obj):
        return '{0} + {1}'.format(*obj._get_primary_and_secondary_gleason())

    @staticmethod
    def get_gleason_4_percentage(obj):
        return obj.get_gleason_4_percentage()
    
    @staticmethod
    def get_largest_confluent_sheet(obj):
        return obj.get_largest_confluent_sheet()
    
    @staticmethod
    def get_total_cribriform_area(obj):
        return obj.get_total_cribriform_area()


class CoreAnnotationDetailsSerializer(CoreAnnotationSerializer):
    core = CoreSerializer(read_only=True)
    
    primary_gleason = serializers.SerializerMethodField()
    secondary_gleason = serializers.SerializerMethodField()
    gleason_group = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()
    
    class Meta:
        model = CoreAnnotation
        fields = CoreAnnotationSerializer.Meta.fields + ('primary_gleason', 'secondary_gleason',
                                                         'gleason_group', 'details')
        
        read_only_fields = CoreAnnotationSerializer.Meta.read_only_fields + ('primary_gleason', 'secondary_gleason',
                                                                             'gleason_group', 'details')
    
    @staticmethod
    def get_primary_gleason(obj):
        return obj.get_primary_gleason()
    
    @staticmethod
    def get_secondary_gleason(obj):
        return obj.get_secondary_gleason()
    
    @staticmethod
    def get_gleason_group(obj):
        return obj.get_gleason_group()
    
    @staticmethod
    def get_details(obj):
        return obj.get_gleason_patterns_details()


class CoreAnnotationInfosSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoreAnnotation
        fields = ('id', 'annotation_step')
        read_only_fields = ('id', 'annotation_step')


class FocusRegionAnnotationSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        model = FocusRegionAnnotation
        fields = ('id', 'author', 'focus_region', 'annotation_step', 'action_start_time', 'action_complete_time',
                  'creation_date', 'perineural_involvement', 'intraductal_carcinoma', 'ductal_carcinoma',
                  'poorly_formed_glands', 'cribriform_pattern', 'small_cell_signet_ring', 'hypernephroid_pattern',
                  'mucinous', 'comedo_necrosis', 'inflammation', 'pah', 'atrophic_lesions', 'adenosis',
                  'cellular_density_helper_json', 'cellular_density', 'cells_count')
        read_only_fields = ('id', 'creation_date')
        write_only_fields = ('annotation_step', 'author')


class GleasonPatternSubregionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GleasonPatternSubregion
        fields = ('id', 'gleason_pattern', 'label', 'roi_json', 'area', 'details_json', 'creation_date')
        read_only_fields = ('id', 'creation_date', 'gleason_pattern')
    
    @staticmethod
    def validate_roi_json(value):
        try:
            json.loads(value)
            return value
        except ValueError:
            raise serializers.ValidationError('Not a valid JSON in \'roi_json\' field')
    
    @staticmethod
    def validate_details_json(value):
        if value is None:
            return value
        try:
            json.loads(value)
            return value
        except ValueError:
            raise serializers.ValidationError('Not a valid JSON in \'details_json\' field')


class GleasonPatternSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    gleason_label = serializers.SerializerMethodField()
    subregions = GleasonPatternSubregionSerializer(many=True)
    
    class Meta:
        model = GleasonPattern
        fields = ('id', 'label', 'focus_region', 'annotation_step', 'author', 'gleason_type', 'gleason_label',
                  'roi_json', 'details_json', 'area', 'subregions',
                  'action_start_time', 'action_complete_time', 'creation_date')
        read_only_fields = ('id', 'creation_date', 'gleason_label')
        write_only_fields = ('annotation_step', 'author')
    
    def create(self, validated_data):
        gleason_subregions_data = validated_data.pop('subregions')
        gleason_pattern_obj = GleasonPattern.objects.create(**validated_data)
        for subregion_data in gleason_subregions_data:
            GleasonPatternSubregion.objects.create(gleason_pattern=gleason_pattern_obj, **subregion_data)
        return gleason_pattern_obj
    
    @staticmethod
    def get_gleason_label(obj):
        return obj.get_gleason_type_label()

    @staticmethod
    def validate_roi_json(value):
        try:
            json.loads(value)
            return value
        except ValueError:
            raise serializers.ValidationError('Not a valid JSON in \'roi_json\' field')
    
    @staticmethod
    def validate_details_json(value):
        if value is None:
            return value
        try:
            json.loads(value)
            return value
        except ValueError:
            raise serializers.ValidationError('Not a valid JSON in \'details_json\' field')


class FocusRegionAnnotationDetailsSerializer(FocusRegionAnnotationSerializer):
    focus_region = FocusRegionSerializer(read_only=True)


class FocusRegionAnnotationInfosSerializer(serializers.ModelSerializer):
    class Meta:
        model = FocusRegionAnnotation
        fields = ('id', 'annotation_step')
        read_only_fields = ('id', 'annotation_step')


class AnnotatedGleasonPatternSerializer(serializers.ModelSerializer):
    class Meta:
        model = GleasonPattern
        fields = ('id', 'label', 'focus_region', 'roi_json', 'area',
                  'annotation_step')


class AnnotatedFocusRegionSerializer(serializers.ModelSerializer):
    clinical_annotations = FocusRegionAnnotationInfosSerializer(many=True)
    gleason_patterns = AnnotatedGleasonPatternSerializer(many=True)

    class Meta:
        model = FocusRegion
        fields = ('id', 'label', 'core', 'roi_json', 'length', 'area',
                  'tissue_status', 'gleason_patterns', 'clinical_annotations')
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
            if fr.is_cancerous_region():
                return True
        return False


class AnnotatedSliceSerializer(serializers.ModelSerializer):
    cores = AnnotatedCoreSerializer(many=True)
    clinical_annotations = SliceAnnotationInfosSerializer(many=True)

    class Meta:
        model = Slice
        fields = ('id', 'label', 'slide', 'roi_json', 'cores', 'clinical_annotations')
        read_only_fields = fields
