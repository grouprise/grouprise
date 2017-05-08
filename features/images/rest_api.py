from django.db.models import Q
from rest_framework import viewsets, mixins, serializers

from core import api
from content import models as content_models
from . import models


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Image
        fields = ('id', 'file', 'title', 'creator', 'path')

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


class ImageSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = ImageSerializer
    filter_fields = ('creator',)

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
        # elif self.action == 'update':
        #     image = self.get_object()
        #     return self.request.user.has_perm('content.update_image', image)
        return False


@api.register
def load(router):
    router.register(r'images', ImageSet, 'image')
