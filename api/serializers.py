from content import models as content_models
from rest_framework import serializers


class Image(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = content_models.Image
        fields = ('file', 'weight')
