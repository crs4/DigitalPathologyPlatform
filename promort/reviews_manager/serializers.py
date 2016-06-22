from django.contrib.auth.models import User

from rest_framework import serializers

from reviews_manager.models import Review, ReviewStep


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        model = Review

        fields = ('id', 'reviewer', 'case', 'creation_date', 'start_date',
                  'completion_date', 'type')
        read_only_fields = ('id', 'creation_date',)


class ReviewStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewStep

        fields = ('id', 'review', 'slide', 'creation_date', 'start_date',
                  'completion_date', 'notes')
        read_only_fields = ('id', 'creation_date',)
