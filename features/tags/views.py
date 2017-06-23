import django
from django.db.models import Q

import core
from features.associations import models as associations
from features.groups import models as groups
from . import forms, models


class Detail(core.views.PermissionMixin, django.views.generic.ListView):
    permission_required = 'tags.view'
    model = associations.Association
    paginate_by = 10
    template_name = 'tags/detail.html'

    def get_queryset(self):
        self.tag = self.get_tag()
        self.groups = groups.Group.objects.filter(tags__tag=self.tag)
        self.tagged_only = int(self.request.GET.get('tagged', 0))
        tagged_query = Q(content__taggeds__tag=self.tag)
        qs = super().get_queryset().ordered_user_content(self.request.user)
        if self.tagged_only:
            qs = qs.filter(tagged_query)
        else:
            group_tagged_query = (
                    Q(entity_type=groups.Group.content_type)
                    & Q(entity_id__in=self.groups))
            qs = qs.filter(tagged_query | group_tagged_query)
        return qs

    def get_tag(self):
        try:
            return models.Tag.objects.get(slug=self.kwargs.get('slug'))
        except models.Tag.DoesNotExist:
            return models.Tag(name=self.kwargs.get('slug'), slug=self.kwargs.get('slug'))


class TagGroup(core.views.PermissionMixin, django.views.generic.CreateView):
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
        try:
            return models.Tag.objects.get(slug=self.kwargs.get('slug'))
        except models.Tag.DoesNotExist:
            return models.Tag(name=self.kwargs.get('slug'), slug=self.kwargs.get('slug'))
