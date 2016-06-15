from . import serializers
from content import models as content_models
from rest_framework import viewsets

class ImageSet(viewsets.ModelViewSet):
    queryset = content_models.Image.objects.all()
    serializer_class = serializers.Image
