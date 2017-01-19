from rest_framework import viewsets, mixins
from django.db.models import Q

from . import serializers, filters
from content import models as content_models
import features.groups.models
import features.gestalten.models


class ImageSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.ImageSerializer
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


class GroupSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.GroupSerializer
    filter_fields = ('id', 'name', )
    filter_class = filters.GroupFilter
    queryset = features.groups.models.Group.objects.all()


class UserSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.UserSerializer
    queryset = features.gestalten.models.Gestalt.objects.all()

    def get_queryset(self):
        user = self.request.user
        return features.gestalten.models.Gestalt.objects.filter(pk=user.gestalt.pk)
