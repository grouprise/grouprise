from . import serializers
from content import models as content_models
from entities import models as entity_models
from features.groups import models as groups
from rest_framework import viewsets, mixins
from django.db.models import Q
from utils.text import slugify


class ImageSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.Image
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


class GroupContentSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.GroupContent
    filter_fields = ('content', )

    def get_queryset(self):
        user = self.request.user
        content = content_models.Content.objects.permitted(user)
        return entity_models.GroupContent.objects.filter(
            Q(content__in=content))

    def create(self, request):
        # TODO: lässt sich der folgende Ablauf irgendwie via content_models.creation ausführen?
        # TODO: sollte der Nutzer als Gruppen-ID oder als Name übergeben werden?
        group = self.request.data.get('group')
        # TODO: ist dies der richtige Weg zur Erzeugung des zugeordneten Objekts ("Article")?
        content_title = self.request.data.get('title', 'Unbekannt')
        content_slug = slugify(content_models.Content, 'slug', bytes(content_title, "utf-8"))
        content_text = self.request.data.get('text')
        try:
            gestalt = self.request.user.gestalt
        except AttributeError:
            gestalt = None
        content = content_models.Article.objects.create(
            title=content_title, text=content_text, slug=content_slug,
            author=gestalt, public=True)
        data = {"user": self.request.user, "content": content.pk, "group": group}
        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            group_content = serializer.save()
            # TODO: was soll zurückgegeben werden?
            return

    def has_permission(self):
        # TODO: soll die Action "list" zulässig sein? Was muss dafür geprüft werden?
        if self.action == 'create':
            group_pk = self.request.data.get('group')
            if group_pk:
                group = groups.Group.objects.get(pk=group_pk)
                # TODO: ist "create_group_message" das richtige Recht?
                return self.request.user.has_perm('entities.create_group_message', group)
            else:
                return False
        elif self.action == 'retrieve':
            content = self.get_object()
            return self.request.user.has_perm('content.view_content', content)
        elif self.action == 'update':
            content = self.get_object()
            return self.request.user.has_perm('content.change_content', content)
        else:
            return False
