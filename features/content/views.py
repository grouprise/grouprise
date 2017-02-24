from content import models as content_models
from core.views import base
from django import shortcuts
from django.contrib.contenttypes import models as contenttypes
from django.views import generic
from features.associations import models as associations
from features.groups import models as groups


class ContentMixin:
    def get_context_data(self, **kwargs):
        kwargs['content'] = self.get_content()
        return super().get_context_data(**kwargs)

    def get_content(self):
        if 'content_pk' in self.kwargs:
            return content_models.Content.objects.get(
                    pk=self.kwargs['content_pk'])
        return None

    def get_grandparent(self, parent):
        if isinstance(parent, content_models.Content):
            if parent.groups.exists():
                return parent.groups.first()
            else:
                return parent.author
        else:
            return None


class Content(base.PermissionMixin, generic.DetailView):
    model = associations.Association
    template_name = 'articles/detail.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            response = super().dispatch(request, *args, **kwargs)
        except self.model.DoesNotExist:
            response = shortcuts.redirect(
                    'content1', self.kwargs['entity_slug'], self.kwargs['association_slug'])
        return response

    def get_object(self, queryset=None):
        entity = shortcuts.get_object_or_404(groups.Group, slug=self.kwargs['entity_slug'])
        queryset = self.get_queryset().filter(
                entity_id=entity.id,
                entity_type=contenttypes.ContentType.objects.get_for_model(entity),
                slug=self.kwargs['association_slug'])
        return queryset.get()

    def has_permission(self):
        self.object = self.get_object()
        if self.request.method == 'GET':
            return self.request.user.has_perms(('content.view',), self.object)
        elif self.request.method == 'POST':
            return self.request.user.has_perms(('content.reply',), self.object)
        else:
            return False
