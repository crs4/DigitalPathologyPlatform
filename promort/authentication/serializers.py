from django.contrib.auth.models import User, Group

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class GroupSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ('name', 'users')

    def get_users(self, obj):
        return [u.username for u in obj.user_set.all()]


class GroupDetailsSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ('name', 'users')

    def get_users(self, obj):
        users = obj.user_set.all()
        serializer = UserSerializer(users, many=True)
        return serializer.data
