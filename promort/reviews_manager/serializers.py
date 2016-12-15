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

    class Meta:
        model = ROIsAnnotation

        fields = ('id', 'reviewer', 'case', 'creation_date', 'start_date',
                  'completion_date', 'steps_count')
        read_only_fields = ('id', 'creation_date', 'steps_count')

    def get_steps_count(self, obj):
        return obj.steps.count()


class ROIsAnnotationsStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ROIsAnnotationStep

        fields = ('id', 'rois_annotation', 'slide', 'creation_date',
                  'start_date', 'completion_date')
        read_only_fields = ('id', 'creation_date')


class ROIsAnnotationsStepDetailsSerializer(ROIsAnnotationsStepSerializer):
    slide = SlideROIsTreeSerializer(many=True, read_only=True)


class ROIsAnnotationDetailsSerializer(serializers.ModelSerializer):
    reviewer = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    steps = ROIsAnnotationsStepSerializer(many=True, read_only=True)

    class Meta:
        model = ROIsAnnotation

        fields = ('id', 'reviewer', 'case', 'creation_date', 'start_date',
                  'completion_date', 'steps')
        read_only_fields = ('id', 'creation_date')


class ClinicalAnnotationSerializer(serializers.ModelSerializer):
    reviewer = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    steps_count = serializers.SerializerMethodField()

    class Meta:
        model = ClinicalAnnotation

        fields = ('id', 'reviewer', 'case', 'rois_review', 'creation_date',
                  'start_date', 'completion_date', 'steps_count')
        read_only_fields = ('id', 'creation_date', 'steps_count')

    def get_steps_count(self, obj):
        return obj.steps.count()


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

    class Meta:
        model = ClinicalAnnotation

        fields = ('id', 'reviewer', 'case', 'rois_review', 'creation_date',
                  'start_date', 'completion_date', 'steps_count')
        read_only_fields = ('id', 'creation_date', 'steps_count')
