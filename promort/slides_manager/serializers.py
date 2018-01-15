from django.contrib.auth.models import User

from rest_framework import serializers

from slides_manager.models import Laboratory, Case, Slide, SlideEvaluation
from reviews_manager.models import ROIsAnnotationStep


class LaboratorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Laboratory

        fields = ('label',)


class CaseSerializer(serializers.ModelSerializer):
    laboratory = serializers.SlugRelatedField(
        slug_field='label',
        queryset=Laboratory.objects.all(),
    )

    class Meta:
        model = Case

        fields = ('id', 'import_date', 'laboratory', 'slides')
        read_only_fields = ('import_date', 'slides')


class SlideSerializer(serializers.ModelSerializer):

    class Meta:
        model = Slide

        fields = ('id', 'case', 'import_date', 'omero_id',
                  'image_type', 'image_microns_per_pixel')
        read_only_fields = ('import_date',)


class SlideEvaluationSerializer(serializers.ModelSerializer):
    reviewer = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
    )
    slide = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Slide.objects.all(),
    )
    rois_annotation_step = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=ROIsAnnotationStep.objects.all()
    )
    not_adequacy_reason_text = serializers.SerializerMethodField()
    staining_text = serializers.SerializerMethodField()

    class Meta:
        model = SlideEvaluation

        fields = ('slide', 'rois_annotation_step', 'staining', 'staining_text', 'adequate_slide', 'not_adequacy_reason',
                  'not_adequacy_reason_text', 'reviewer', 'acquisition_date', 'notes')
        read_only_fields = ('acquisition_date', 'staining_text', 'not_adequacy_reason_text')

    @staticmethod
    def get_not_adequacy_reason_text(obj):
        return obj.get_not_adequacy_reason_text()

    @staticmethod
    def get_staining_text(obj):
        return obj.get_staining_text()


class LaboratoryDetailSerializer(serializers.ModelSerializer):
    cases = CaseSerializer(many=True, read_only=True)

    class Meta:
        model = Laboratory

        fields = ('label', 'cases')
        read_only_fields = ('cases',)


class CaseDetailedSerializer(serializers.ModelSerializer):
    slides = SlideSerializer(many=True, read_only=True)

    class Meta:
        model = Case

        fields = ('id', 'import_date', 'slides')
        read_only_fields = ('import_date',)


class SlideDetailSerializer(serializers.ModelSerializer):
    case = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Slide

        fields = ('id', 'case', 'import_date', 'omero_id',
                  'image_type', 'image_microns_per_pixel')
        read_only_fields = ('import_date',)

