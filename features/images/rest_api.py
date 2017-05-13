from rest_framework import viewsets, mixins, serializers
from sorl.thumbnail import get_thumbnail

import django_filters
import django_filters.widgets

from core import api
from . import models


class ImageFilter(django_filters.rest_framework.FilterSet):
    id = django_filters.Filter(name='id', lookup_expr='in',
                               widget=django_filters.widgets.CSVWidget)

    class Meta:
        model = models.Image
        fields = ('id', 'creator')


class ImageSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='file.name', read_only=True)
    path = serializers.CharField(source='file.url', read_only=True)

    class Meta:
        model = models.Image
        fields = ('id', 'file', 'title', 'creator', 'path')

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

    def to_representation(self, instance: models.Image):
        repr = super().to_representation(instance)
        repr['preview'] = get_thumbnail(instance.file, '250x250', crop='center', format='PNG').url
        return repr


class ImageSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = ImageSerializer
    filter_fields = ('id', 'creator')
    filter_class = ImageFilter

    def get_queryset(self):
        user = self.request.user
        return models.Image.objects.filter(creator__user=user)

    def has_permission(self):
        if self.action == 'create':
            return True
        elif self.action == 'list':
            return True
        elif self.action == 'retrieve':
            image = self.get_object()
            return self.request.user.has_perm('images.view', image)
        elif self.action == 'update':
            image = self.get_object()
            return image.creator == self.request.user
        return False


@api.register
def load(router):
    router.register(r'images', ImageSet, 'image')
