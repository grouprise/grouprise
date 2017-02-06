from rest_framework import viewsets, mixins, serializers
from content import models as content_models
from django.db.models import Q
from features.rest_api import api


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


class ImageSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = ImageSerializer
    filter_fields = ('content', 'creator', )

    def get_queryset(self):
        user = self.request.user
        content = content_models.Content.objects.permitted(user)
        try:
            gestalt = user.gestalt
        except AttributeError:
            gestalt = None
        return content_models.Image.objects.filter(
            Q(content__in=content) | Q(creator=gestalt)).order_by('-weight')

    def has_permission(self):
        if self.action == 'create':
            content_pk = self.request.data.get('content')
            if content_pk:
                content = content_models.Content.objects.get(pk=content_pk)
                return self.request.user.has_perm('content.create_image', content)
            return True
        elif self.action == 'list':
            return True
        elif self.action == 'retrieve':
            image = self.get_object()
            return self.request.user.has_perm('content.view_image', image)
        elif self.action == 'update':
            image = self.get_object()
            return self.request.user.has_perm('content.update_image', image)
        return False


@api.register
def load(router):
    router.register(r'images', ImageSet, 'image')
