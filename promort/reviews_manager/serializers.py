from django.contrib.auth.models import User

from rest_framework import serializers

from reviews_manager.models import ROIsAnnotation, ROIsAnnotationStep,\
    ClinicalAnnotation, ClinicalAnnotationStep
from slides_manager.serializers import SlideSerializer, SlideEvaluationSerializer
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

        fields = ('id', 'label', 'annotation_type', 'reviewer', 'case', 'started', 'completed',
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
    can_reopen = serializers.SerializerMethodField()
    started = serializers.SerializerMethodField()
    completed = serializers.SerializerMethodField()
    slide_evaluation = SlideEvaluationSerializer(read_only=True)

    class Meta:
        model = ROIsAnnotationStep

        fields = ('id', 'label', 'rois_annotation', 'slide', 'creation_date', 'started', 'completed',
                  'can_reopen', 'start_date', 'completion_date', 'slide_evaluation')
        read_only_fields = ('id', 'creation_date', 'started', 'completed')

    @staticmethod
    def get_can_reopen(obj):
        return obj.can_reopen()

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

        fields = ('id', 'label', 'rois_annotation', 'slide', 'creation_date', 'started', 'completed',
                  'start_date', 'completion_date', 'slide_evaluation', 'slices')
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

        fields = ('id', 'label', 'annotation_type', 'reviewer', 'case', 'started', 'completed',
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

        fields = ('id', 'label', 'annotation_type', 'reviewer', 'case', 'rois_review',
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
    rois_review_step_label = serializers.SerializerMethodField()
    case = serializers.SerializerMethodField()
    rois_step_reopen_permission = serializers.SerializerMethodField()
    can_reopen_rois_step = serializers.SerializerMethodField()
    slide_evaluation = serializers.SerializerMethodField()

    class Meta:
        model = ClinicalAnnotationStep

        fields = ('id', 'label', 'clinical_annotation', 'slide', 'case', 'rois_review_step',
                  'rois_review_step_label', 'started', 'completed', 'can_be_started',
                  'creation_date', 'start_date', 'completion_date', 'rejected', 'rejection_reason',
                  'notes', 'rois_step_reopen_permission', 'can_reopen_rois_step', 'slide_evaluation')
        read_only_fields = ('id', 'case', 'creation_date', 'started', 'completed', 'rois_review_step_label',
                            'can_be_started', 'slide_evaluation')

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
    def get_rois_review_step_label(obj):
        return obj.rois_review_step.label

    @staticmethod
    def get_case(obj):
        return obj.slide.case.id

    def get_rois_step_reopen_permission(self, obj):
        username = self.context.get('current_user')
        return obj.rois_review_step.has_reopen_permission(username)

    @staticmethod
    def get_can_reopen_rois_step(obj):
        return obj.rois_review_step.can_reopen()

    @staticmethod
    def get_slide_evaluation(obj):
        return SlideEvaluationSerializer(obj.rois_review_step.slide_evaluation).data


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

        fields = ('id', 'label', 'annotation_type', 'reviewer', 'case', 'rois_review',
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
