from content import models as content_models
from rest_framework import serializers


class Image(serializers.ModelSerializer):
    title = serializers.CharField(source='file.name', read_only=True)

    class Meta:
        model = content_models.Image
        fields = ('id', 'file', 'weight', 'content', 'title')
