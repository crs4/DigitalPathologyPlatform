from rest_framework import serializers

from slides_manager.models import Case, Slide


class CaseSerializer(serializers.ModelSerializer):
    slides = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Case

        fields = ('id', 'import_date', 'slides')
        read_only_fields = ('import_date', 'slides')


class SlideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slide

        fields = ('id', 'case', 'import_date', 'omero_id', 'image_type')
        read_only_fields = ('import_date',)


class CaseDetailedSerializer(serializers.ModelSerializer):
    slides = SlideSerializer(many=True, read_only=True)

    class Meta:
        model = Case

        fields = ('id', 'import_date', 'slides')
        read_only_fields = ('import_date', 'slides')


class SlideDetailSerializer(serializers.ModelSerializer):
    case = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Slide
        fields = ('id', 'case', 'import_date', 'omero_id', 'image_type')
        read_only_fields = ('import_date',)
