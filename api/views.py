from . import serializers
from content import models as content_models
from rest_framework import viewsets, mixins
from django.db.models import Q


class ImageSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.Image
    filter_fields = ('content', 'creator', )

    def get_queryset(self):
        user = self.request.user
        content = content_models.Content.objects.permitted(user)
        return content_models.Image.objects.filter(Q(content__in=content) | Q(creator=user.gestalt)).order_by('-weight')

    def has_permission(self):
        if self.action == 'create':
            content_pk = self.request.data.get('content')
            if content_pk:
                content = content_models.Content.objects.get(pk=content_pk)
                return self.request.user.has_perm('content.create_image', content)
            return False
        elif self.action == 'list':
            return True
        elif self.action == 'retrieve':
            image = self.get_object()
            return self.request.user.has_perm('content.view_image', image)
        elif self.action == 'update':
            image = self.get_object()
            return self.request.user.has_perm('content.update_image', image)
        return False
