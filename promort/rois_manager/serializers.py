from django.contrib.auth.models import User

from rest_framework import serializers

from rois_manager.models import Slice, Core, CellularFocus


class SliceSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    cores_count = serializers.SerializerMethodField()

    class Meta:
        model = Slice
        fields = ('id', 'label', 'slide', 'author', 'creation_date', 'roi_json',
                  'total_cores', 'positive_cores', 'cores_count')
        read_only_fields = ('id', 'creation_date', 'cores_count')

    def get_cores_count(self, obj):
        return obj.cores.count()


class CoreSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    cellular_focuses_count = serializers.SerializerMethodField()

    class Meta:
        model = Core
        fields = ('id', 'label', 'slice', 'author', 'creation_date', 'roi_json',
                  'length', 'area', 'cellular_focuses_count')
        read_only_fields = ('id', 'creation_date', 'cellular_focuses_count')

    def get_cellular_focuses_count(self, obj):
        return obj.cellular_focuses.count()


class CelluarFocusSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        model = CellularFocus
        fields = ('id', 'label', 'core', 'author', 'creation_date', 'roi_json'
                  'length', 'area', 'cancerous_region')
        read_only_fields = ('id', 'creation_date',)


class CoreDetailsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    cellular_focuses = CelluarFocusSerializer(many=True, read_only=True)

    class Meta:
        model = Core
        fields = ('id', 'label', 'slice', 'author', 'creation_date',
                  'roi_json', 'length', 'area', 'cellular_focuses')
        read_only_fields = ('id', 'creation_date')


class SliceDetailsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    cores = CoreDetailsSerializer(many=True, read_only=True)

    class Meta:
        model = Slice
        fields = ('id', 'label', 'slide', 'author', 'creation_date',
                  'roi_json', 'total_cores', 'positive_cores', 'cores')
        read_only_fields = ('id', 'creation_date')
