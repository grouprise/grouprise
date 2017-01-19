from content import models as content_models
import features.groups.models
import features.tags.models
import features.gestalten.models
from rest_framework import serializers


class ImageSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='file.name', read_only=True)
    path = serializers.CharField(source='file.url', read_only=True)

    def _get_gestalt(self):
        try:
            return self.context['request'].user.gestalt
        except AttributeError:
            return None

    def create(self, validated_data):
        validated_data.update({"creator": self._get_gestalt()})
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.update({"creator": self._get_gestalt()})
        return super().update(instance, validated_data)

    class Meta:
        model = content_models.Image
        fields = ('id', 'file', 'weight', 'content', 'title', 'creator', 'path')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = features.tags.models.Tag
        fields = ('id', 'name')


class GroupSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    initials = serializers.CharField(source='get_initials', read_only=True)

    class Meta:
        model = features.groups.models.Group
        fields = ('id', 'name', 'initials', 'description', 'avatar', 'avatar_color', 'tags')


class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='__str__', read_only=True)
    initials = serializers.CharField(source='get_initials', read_only=True)

    class Meta:
        model = features.gestalten.models.Gestalt
        fields = ('id', 'name', 'initials', 'about', 'avatar', 'avatar_color')
