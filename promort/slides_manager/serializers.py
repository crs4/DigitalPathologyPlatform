from django.contrib.auth.models import User

from rest_framework import serializers

from slides_manager.models import Case, Slide, \
    SlideQualityControl


class CaseSerializer(serializers.ModelSerializer):
    slides = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Case

        fields = ('id', 'import_date', 'slides')
        read_only_fields = ('import_date', 'slides')


class SlideSerializer(serializers.ModelSerializer):

    class Meta:
        model = Slide

        fields = ('id', 'case', 'import_date', 'omero_id',
                  'image_type', 'image_microns_per_pixel', 'staining')
        read_only_fields = ('import_date',)


class SlideQualityControlSerializer(serializers.ModelSerializer):
    reviewer = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
    )
    slide = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Slide.objects.all(),
    )

    class Meta:
        model = SlideQualityControl

        fields = ('slide', 'rois_annotation_step', 'adequate_slide', 'not_adequacy_reason',
                  'reviewer', 'acquisition_date', 'notes')
        read_only_fields = ('acquisition_date',)
        write_only_fields = ('rois_annotation_step',)


class CaseDetailedSerializer(serializers.ModelSerializer):
    slides = SlideSerializer(many=True, read_only=True)

    class Meta:
        model = Case

        fields = ('id', 'import_date', 'slides')
        read_only_fields = ('import_date',)


class SlideDetailSerializer(serializers.ModelSerializer):
    case = serializers.PrimaryKeyRelatedField(read_only=True)
    quality_control = SlideQualityControlSerializer(read_only=True,
                                                    source='quality_control_passed')

    class Meta:
        model = Slide

        fields = ('id', 'case', 'import_date', 'omero_id',
                  'image_type', 'quality_control',
                  'image_microns_per_pixel', 'staining')
        read_only_fields = ('import_date',)

