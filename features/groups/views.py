"""
Copyright 2016-2017 sense.lab e.V. <info@senselab.org>

This file is part of stadtgestalten.

stadtgestalten is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

stadtgestalten is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero Public License for more details.

You should have received a copy of the GNU Affero Public License
along with stadtgestalten.  If not, see <http://www.gnu.org/licenses/>.
"""

from django.views import generic
from django_filters import views as filters_views

from entities import filters
from content import models as content_models
from core import fields, views
from core.views import base
from features.associations import models as associations
from features.groups import models as groups
from . import forms, models


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
            if 'content_pk' in self.kwargs:
                return content_models.Content.objects.get(
                        pk=self.kwargs['content_pk']).groups.first()
        except (content_models.Content.DoesNotExist,
                models.Group.DoesNotExist):
            pass
        return None


class Create(views.Create):
    permission_required = 'groups.create_group'

    action = 'Gruppe anlegen'
    menu = 'group'
    parent = 'group-index'
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
        return associations.Association.objects.filter(
                entity_type=groups.Group.content_type).can_view(self.request.user)

    def get_queryset(self):
        return groups.Group.objects.order_by('-score')


class Update(base.PermissionMixin, generic.UpdateView):
    permission_required = 'groups.change_group'
    model = models.Group
    template_name = 'groups/update.html'

    form_class = forms.Update
