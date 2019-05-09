from rest_framework import serializers

from . import models


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ('id', 'name')


class FlattenedTagSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='tag.id', read_only=True)
    name = serializers.CharField(source='tag.name', read_only=True)

    class Meta:
        model = models.Tagged
        fields = ('id', 'name')
