import django
from django.db.models import Q
from django.views.generic import ListView

import grouprise.core
from grouprise.core.views import PermissionMixin, TemplateFilterMixin
from grouprise.features.associations import models as associations
from grouprise.features.groups import models as groups
from grouprise.features.tags.filters import TagContentFilterSet
from . import forms, models


class Detail(PermissionMixin, TemplateFilterMixin, ListView):
    permission_required = 'tags.view'
    model = associations.Association
    filterset_class = TagContentFilterSet
    paginate_by = 10
    template_name = 'tags/detail.html'

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)
        kwargs['tag'] = self.tag
        return kwargs

    def get_queryset(self):
        self.tag = self.get_tag()
        self.groups = groups.Group.objects.filter(tags__tag=self.tag)
        tagged_content_query = Q(content__taggeds__tag=self.tag)
        tagged_group_content_query = (
                Q(entity_type=groups.Group.content_type)
                & Q(entity_id__in=self.groups))
        return super().get_queryset().ordered_user_content(self.request.user) \
            .filter(tagged_content_query | tagged_group_content_query)

    def get_tag(self):
        try:
            return models.Tag.objects.get(slug=self.kwargs.get('slug'))
        except models.Tag.DoesNotExist:
            return models.Tag(name=self.kwargs.get('slug'), slug=self.kwargs.get('slug'))


class TagGroup(grouprise.core.views.PermissionMixin, django.views.generic.CreateView):
    permission_required = 'tags.tag_group'
    form_class = forms.TagGroup
    template_name = 'tags/tag_group.html'

    def get_form_kwargs(self):
        self.tag = self.get_tag()
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = models.Tagged(tag=self.tag)
        kwargs['tagger'] = self.request.user.gestalt
        return kwargs

    def get_permission_object(self):
        return None

    def get_success_url(self):
        return self.tag.get_absolute_url()

    def get_tag(self):
        slug = self.kwargs.get('slug')
        tag, created = models.Tag.objects.get_or_create(slug=slug, defaults={'name': slug})
        return tag
