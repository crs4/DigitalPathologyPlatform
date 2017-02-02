from django.contrib.auth.models import User

from rest_framework import serializers

from reviews_manager.models import ROIsAnnotation, ROIsAnnotationStep,\
    ClinicalAnnotation, ClinicalAnnotationStep
from rois_manager.serializers import SlideROIsTreeSerializer


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
    class Meta:
        model = ROIsAnnotationStep

        fields = ('id', 'rois_annotation', 'slide', 'creation_date',
                  'start_date', 'completion_date')
        read_only_fields = ('id', 'creation_date')


class ROIsAnnotationStepDetailsSerializer(ROIsAnnotationsStepSerializer):
    slide = SlideROIsTreeSerializer(many=True, read_only=True)


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
        obj.can_be_started()

    @staticmethod
    def get_annotation_type(obj):
        return 'CLINICAL_ANNOTATION'


class ClinicalAnnotationStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalAnnotationStep

        fields = ('id', 'clinical_annotation', 'slide', 'rois_review_step',
                  'creation_date', 'start_date', 'completion_date', 'notes')
        read_only_fields = ('id', 'creation_date')


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
                  'started', 'completed', 'can_be_started',
                  'creation_date', 'start_date', 'completion_date', 'steps_count')
        read_only_fields = ('id', 'creation_date', 'steps_count',
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
