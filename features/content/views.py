import django.core.urlresolvers
from django import shortcuts
from django.contrib.contenttypes import models as contenttypes
from django.views import generic
from django.views.generic import edit

from . import forms, models
from content import models as content_models
from core.views import base
from features.associations import models as associations
from features.contributions import views as contributions
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


class Content(base.PermissionMixin, contributions.ContributionFormMixin, generic.DetailView):
    permission_required = 'content.view'
    model = associations.Association
    template_name = 'articles/detail.html'

    form_class = forms.Comment

    def get_object(self, queryset=None):
        entity = shortcuts.get_object_or_404(groups.Group, slug=self.kwargs['entity_slug'])
        return shortcuts.get_object_or_404(
                self.model,
                entity_id=entity.id,
                entity_type=contenttypes.ContentType.objects.get_for_model(entity),
                slug=self.kwargs['association_slug'])

    def get_success_url(self):
        return django.core.urlresolvers.reverse(
                'content', args=[self.object.entity.slug, self.object.slug])

    def has_permission(self):
        self.object = self.get_object()
        if self.request.method == 'GET':
            return self.request.user.has_perms((self.permission_required,), self.object)
        elif self.request.method == 'POST':
            return self.request.user.has_perms(('content.comment',), self.object)
        else:
            return False


class CreateVersion(base.PermissionMixin, generic.CreateView):
    permission_required = 'content.create_version'
    model = models.Version
    form_class = forms.CreateVersion
    template_name = 'content/create_version.html'

    def get_permission_object(self):
        entity = shortcuts.get_object_or_404(groups.Group, slug=self.kwargs['entity_slug'])
        self.association = shortcuts.get_object_or_404(
                associations.Association,
                entity_id=entity.id,
                entity_type=contenttypes.ContentType.objects.get_for_model(entity),
                slug=self.kwargs['association_slug'])
        return self.association
