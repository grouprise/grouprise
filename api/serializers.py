from content import models as content_models
from entities import models as entity_models
from rest_framework import serializers


class Image(serializers.ModelSerializer):
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


class GroupContent(serializers.ModelSerializer):

    class Meta:
        model = entity_models.GroupContent
        fields = ('content', 'group', 'pinned')
