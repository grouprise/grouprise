from content import models as content_models
from rest_framework import serializers


class Image(serializers.ModelSerializer):
    title = serializers.CharField(source='file.name', read_only=True)

    def create(self, validated_data):
        validated_data.update({"creator": self.context['request'].user.gestalt})
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.update({"creator": self.context['request'].user.gestalt})
        return super().update(instance, validated_data)

    class Meta:
        model = content_models.Image
        fields = ('id', 'file', 'weight', 'content', 'title', 'creator')
