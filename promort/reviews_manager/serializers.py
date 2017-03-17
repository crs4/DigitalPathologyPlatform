from django.contrib.auth.models import User

from rest_framework import serializers

from reviews_manager.models import ROIsAnnotation, ROIsAnnotationStep,\
    ClinicalAnnotation, ClinicalAnnotationStep
from slides_manager.serializers import SlideSerializer, SlideQualityControlSerializer
from rois_manager.serializers import SliceSerializer, SliceROIsTreeSerializer
from clinical_annotations_manager.serializers import AnnotatedSliceSerializer


class ROIsAnnotationSerializer(serializers.ModelSerializer):
    reviewer = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    steps_count = serializers.SerializerMethodField()
    started = serializers.SerializerMethodField()
    completed = serializers.SerializerMethodField()
    annotation_type = serializers.SerializerMethodField()

    class Meta:
        model = ROIsAnnotation

        fields = ('id', 'annotation_type', 'reviewer', 'case', 'started', 'completed',
                  'creation_date', 'start_date', 'completion_date', 'steps_count')
        read_only_fields = ('id', 'creation_date', 'steps_count', 'started',
                            'completed', 'annotation_type')

    @staticmethod
    def get_steps_count(obj):
        return obj.steps.count()

    @staticmethod
    def get_started(obj):
        return obj.is_started()

    @staticmethod
    def get_completed(obj):
        return obj.is_completed()

    @staticmethod
    def get_annotation_type(obj):
        return 'ROIS_ANNOTATION'


class ROIsAnnotationStepSerializer(serializers.ModelSerializer):
    started = serializers.SerializerMethodField()
    completed = serializers.SerializerMethodField()
    slide_quality_control = SlideQualityControlSerializer(read_only=True)

    class Meta:
        model = ROIsAnnotationStep

        fields = ('id', 'rois_annotation', 'slide', 'creation_date', 'started', 'completed',
                  'start_date', 'completion_date', 'slide_quality_control')
        read_only_fields = ('id', 'creation_date', 'started', 'completed')

    @staticmethod
    def get_started(obj):
        return obj.is_started()

    @staticmethod
    def get_completed(obj):
        return obj.is_completed()


class ROIsAnnotationStepDetailsSerializer(ROIsAnnotationStepSerializer):
    slide = SlideSerializer(read_only=True)


class ROIsAnnotationStepFullSerializer(ROIsAnnotationStepDetailsSerializer):
    slices = SliceSerializer(many=True, read_only=True)

    class Meta:
        model = ROIsAnnotationStep

        fields = ('id', 'rois_annotation', 'slide', 'creation_date', 'started', 'completed',
                  'start_date', 'completion_date', 'slide_quality_control', 'slices')
        read_only_fields = ('id', 'creation_date', 'started', 'completed')


class ROIsAnnotationStepROIsTreeSerializer(ROIsAnnotationStepFullSerializer):
    slices = SliceROIsTreeSerializer(many=True, read_only=True)


class ClinicalAnnotationStepROIsTreeSerializer(ROIsAnnotationStepFullSerializer):
    slices = AnnotatedSliceSerializer(many=True, read_only=True)


class ROIsAnnotationDetailsSerializer(serializers.ModelSerializer):
    reviewer = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    steps = ROIsAnnotationStepSerializer(many=True, read_only=True)
    started = serializers.SerializerMethodField()
    completed = serializers.SerializerMethodField()
    annotation_type = serializers.SerializerMethodField()

    class Meta:
        model = ROIsAnnotation

        fields = ('id', 'annotation_type', 'reviewer', 'case', 'started', 'completed',
                  'creation_date', 'start_date', 'completion_date', 'steps')
        read_only_fields = ('id', 'creation_date', 'started', 'completed',
                            'annotation_type')

    @staticmethod
    def get_started(obj):
        return obj.is_started()

    @staticmethod
    def get_completed(obj):
        return obj.is_completed()

    @staticmethod
    def get_annotation_type(obj):
        return 'ROIS_ANNOTATION'


class ClinicalAnnotationSerializer(serializers.ModelSerializer):
    reviewer = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    steps_count = serializers.SerializerMethodField()
    started = serializers.SerializerMethodField()
    completed = serializers.SerializerMethodField()
    can_be_started = serializers.SerializerMethodField()
    annotation_type = serializers.SerializerMethodField()

    class Meta:
        model = ClinicalAnnotation

        fields = ('id', 'annotation_type', 'reviewer', 'case', 'rois_review',
                  'started', 'completed', 'can_be_started',
                  'creation_date', 'start_date', 'completion_date', 'steps_count')
        read_only_fields = ('id', 'creation_date', 'steps_count', 'started',
                            'completed', 'can_be_started', 'annotation_type')

    @staticmethod
    def get_steps_count(obj):
        return obj.steps.count()

    @staticmethod
    def get_started(obj):
        return obj.is_started()

    @staticmethod
    def get_completed(obj):
        return obj.is_completed()

    @staticmethod
    def get_can_be_started(obj):
        return obj.can_be_started()

    @staticmethod
    def get_annotation_type(obj):
        return 'CLINICAL_ANNOTATION'


class ClinicalAnnotationStepSerializer(serializers.ModelSerializer):
    started = serializers.SerializerMethodField()
    completed = serializers.SerializerMethodField()
    can_be_started = serializers.SerializerMethodField()

    class Meta:
        model = ClinicalAnnotationStep

        fields = ('id', 'clinical_annotation', 'slide', 'rois_review_step',
                  'started', 'completed', 'can_be_started',
                  'creation_date', 'start_date', 'completion_date', 'notes')
        read_only_fields = ('id', 'creation_date', 'started', 'completed',
                            'can_be_started')

    @staticmethod
    def get_started(obj):
        return obj.is_started()

    @staticmethod
    def get_completed(obj):
        return obj.is_completed()

    @staticmethod
    def get_can_be_started(obj):
        return obj.can_be_started()


class ClinicalAnnotationDetailsSerializer(serializers.ModelSerializer):
    reviewer = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    steps = ClinicalAnnotationStepSerializer(many=True, read_only=True)
    started = serializers.SerializerMethodField()
    completed = serializers.SerializerMethodField()
    can_be_started = serializers.SerializerMethodField()
    annotation_type = serializers.SerializerMethodField()

    class Meta:
        model = ClinicalAnnotation

        fields = ('id', 'annotation_type', 'reviewer', 'case', 'rois_review',
                  'started', 'completed', 'can_be_started', 'steps',
                  'creation_date', 'start_date', 'completion_date')
        read_only_fields = ('id', 'creation_date', 'steps',
                            'started', 'completed', 'can_be_started', 'annotation_type')

    @staticmethod
    def get_started(obj):
        return obj.is_started()

    @staticmethod
    def get_completed(obj):
        return obj.is_completed()

    @staticmethod
    def get_can_be_started(obj):
        return obj.can_be_started()

    @staticmethod
    def get_annotation_type(obj):
        return 'CLINICAL_ANNOTATION'
