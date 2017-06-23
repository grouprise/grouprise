import django
from django.views import generic
from django_filters import views as filters_views

import utils
from core import fields, views
from core.views import base
from features.associations import models as associations
from features.content import models as content
from features.groups import models as groups
from . import filters, forms, models


class Mixin:
    def get_context_data(self, **kwargs):
        kwargs['group'] = self.get_group()
        return super().get_context_data(**kwargs)

    def get_group(self):
        for attr in ('object', 'related_object'):
            if hasattr(self, attr):
                instance = getattr(self, attr)
                if isinstance(instance, models.Group):
                    return instance
                if hasattr(instance, 'group'):
                    return instance.group
                if hasattr(instance, 'groups'):
                    return instance.groups.first()
        try:
            if 'group_pk' in self.kwargs:
                return models.Group.objects.get(
                        pk=self.kwargs['group_pk'])
            if 'group_slug' in self.kwargs:
                return models.Group.objects.get(
                        slug=self.kwargs['group_slug'])
            if 'group' in self.request.GET:
                return models.Group.objects.get(
                        slug=self.request.GET['group'])
        except models.Group.DoesNotExist:
            pass
        return None


class Create(views.Create):
    permission_required = 'groups.create_group'

    action = 'Gruppe anlegen'
    menu = 'group'
    # parent = 'group-index'
    title = 'Neue Gruppe'

    model = models.Group

    data_field_classes = (
            fields.current_gestalt('gestalt_created', null=True),
            fields.model_field('name'))


class List(base.PermissionMixin, filters_views.FilterView):
    permission_required = 'groups.view_list'
    filterset_class = filters.Group
    paginate_by = 10

    def get_content(self):
        return associations.Association.objects.filter_group_containers().can_view(
                self.request.user)

    def get_queryset(self):
        return groups.Group.objects.order_by('-score')


class Update(base.PermissionMixin, generic.UpdateView):
    permission_required = 'groups.change_group'
    model = models.Group
    template_name = 'groups/update.html'

    form_class = forms.Update


class GroupAvatarUpdate(utils.views.ActionMixin, django.views.generic.UpdateView):
    action = 'Avatar ändern'
    fields = ('avatar',)
    layout = ('avatar',)
    menu = 'group'
    model = models.Group
    permission_required = 'groups.change_group'

    def get_parent(self):
        return self.object


class GroupLogoUpdate(utils.views.ActionMixin, django.views.generic.UpdateView):
    action = 'Logo ändern'
    fields = ('logo',)
    layout = ('logo',)
    menu = 'group'
    model = models.Group
    permission_required = 'groups.change_group'

    def get_parent(self):
        return self.object


class Group(utils.views.List):
    menu = 'group'
    permission_required = 'entities.view_group'
    template_name = 'entities/group_detail.html'

    def get(self, *args, **kwargs):
        if not self.get_group():
            raise django.http.Http404('Gruppe nicht gefunden')
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['intro_content'] = self.get_intro_content()
        return super().get_context_data(**kwargs)

    def get_group_content(self):
        group = self.get_group()
        return associations.Association.objects.filter(
                container_type=content.Content.content_type,
                entity_type=models.Group.content_type,
                entity_id=group.id
                ).can_view(self.request.user)

    def get_intro_content(self):
        pinned_content = self.get_group_content().filter(pinned=True).annotate(
                time_created=django.db.models.Min('content__versions__time_created')
                ).order_by('time_created')
        try:
            return pinned_content.exclude(pk=self.get_group().get_head_gallery().pk)
        except AttributeError:
            return pinned_content

    def get_queryset(self):
        return self.get_group_content().filter(pinned=False).annotate(
                time_created=django.db.models.Min(
                    'content__versions__time_created')).order_by('-time_created')

    def get_related_object(self):
        return self.get_group()

    def get_title(self):
        return self.get_group().name
