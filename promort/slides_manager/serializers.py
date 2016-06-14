from rest_framework import serializers

from slides_manager.models import Case, Slide


class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case

        fields = ('id', 'import_date')
        read_only_fields = ('import_date',)


class SlideSerializer(serializers.ModelSerializer):
    case = CaseSerializer(read_only=True, required=False)

    class Meta:
        model = Slide

        fields = ('id', 'case', 'import_date', 'omero_id', 'image_type')
        read_only_fields = ('import_date',)

    def get_validation_exclusion(self, *args, **kwargs):
        exclusions = super(SlideSerializer, self).get_validation_exclusions()
        return exclusions + ['case']
