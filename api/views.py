from . import serializers
from content import models as content_models
from rest_framework import viewsets, mixins, filters


class ImageSet(viewsets.ReadOnlyModelViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    queryset = content_models.Image.objects.all().order_by("-weight")
    serializer_class = serializers.Image
    filter_backends = (filters.DjangoFilterBackend, )
    filter_fields = ("content", )
