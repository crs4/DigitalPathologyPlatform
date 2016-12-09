from django.contrib.auth.models import User

from rest_framework import serializers

from reviews_manager.models import ROIsAnnotation, ROIsAnnotationStep, Review, ReviewStep


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    steps_count = serializers.SerializerMethodField()

    class Meta:
        model = Review

        fields = ('id', 'reviewer', 'case', 'creation_date', 'start_date',
                  'completion_date', 'type', 'steps_count')
        read_only_fields = ('id', 'creation_date', 'steps_count',)

    def get_steps_count(self, obj):
        return obj.steps.count()


class ReviewStepSerializer(serializers.ModelSerializer):
    review_type = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ReviewStep

        fields = ('id', 'review', 'review_type', 'slide', 'creation_date',
                  'start_date', 'completion_date', 'notes')
        read_only_fields = ('id', 'creation_date',)

    def get_review_type(self, obj):
        rev = obj.review
        return rev.type


class ReviewDetailsSerializer(serializers.ModelSerializer):
    reviewer = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    steps = ReviewStepSerializer(many=True, read_only=True)

    class Meta:
        model = Review

        fields = ('id', 'reviewer', 'case', 'creation_date', 'start_date',
                  'completion_date', 'type', 'steps')
        read_only_fields = ('id', 'creation_date')


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
