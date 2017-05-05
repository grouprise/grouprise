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

import django.db.models
from django import http
from django.contrib.contenttypes import models as contenttypes
from django.utils import six
from django.views import generic
from crispy_forms import layout

from utils import forms as utils_forms, views as utils_views
from content import models as content_models
from features.associations import models as associations
from features.content import models as content2
from features.gestalten import models as gestalten
from features.groups import models as groups
from . import forms


class Gestalt(utils_views.List):
    menu = 'gestalt'
    model = associations.Association
    permission_required = 'entities.view_gestalt'
    sidebar = ('calendar',)
    template_name = 'entities/gestalt_detail.html'

    def get(self, request, *args, **kwargs):
        if not self.get_gestalt():
            raise http.Http404('Gestalt nicht gefunden')
        return super().get(request, *args, **kwargs)

    def get_permission_object(self):
        return self.get_gestalt()

    def get_queryset(self):
        return super().get_queryset().filter(
                container_type=content2.Content.content_type,
                entity_type=self.get_gestalt().get_content_type(),
                entity_id=self.get_gestalt().id
                ).can_view(self.request.user).annotate(time_created=django.db.models.Min(
                    'content__versions__time_created')).order_by('-time_created')

    def get_title(self):
        return str(self.get_gestalt())


class GestaltUpdate(utils_views.ActionMixin, generic.UpdateView):
    action = 'Dein Profil'
    form_class = forms.Gestalt
    menu = 'gestalt'
    message = 'Die Einstellungen wurden geändert.'
    model = gestalten.Gestalt
    permission_required = 'entities.change_gestalt'

    def get_parent(self):
        return self.object


class GestaltAvatarUpdate(utils_views.ActionMixin, generic.UpdateView):
    action = 'Avatar ändern'
    fields = ('avatar',)
    layout = ('avatar',)
    menu = 'gestalt'
    model = gestalten.Gestalt
    permission_required = 'entities.change_gestalt'

    def get_parent(self):
        return self.object


class GestaltBackgroundUpdate(utils_views.ActionMixin, generic.UpdateView):
    action = 'Hintergrundbild ändern'
    fields = ('background',)
    layout = ('background',)
    menu = 'gestalt'
    model = gestalten.Gestalt
    permission_required = 'entities.change_gestalt'

    def get_parent(self):
        return self.object


class Group(utils_views.List):
    menu = 'group'
    permission_required = 'entities.view_group'
    template_name = 'entities/group_detail.html'

    def get(self, *args, **kwargs):
        if not self.get_group():
            raise http.Http404('Gruppe nicht gefunden')
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['intro_content'] = self.get_intro_content()
        return super().get_context_data(**kwargs)

    def get_events(self):
        return content_models.Event.objects.can_view(self.request.user).filter(
                groups=self.get_group())

    def get_group_content(self):
        group = self.get_group()
        return associations.Association.objects.filter(
                container_type=contenttypes.ContentType.objects.get_for_model(content2.Content),
                entity_type=contenttypes.ContentType.objects.get_for_model(groups.Group),
                entity_id=group.id
                ).can_view(self.request.user)

    def get_inline_view_form(self):
        # FIXME: hacky code follows
        if (self.request.user.has_perm('entities.create_group_content', self.get_group())
                and not self.get_group().get_head_gallery()):
            form = super().get_inline_view_form()
            form.helper.filter(six.string_types).wrap(layout.Field)
            form.helper.filter(layout.Field).update_attributes(
                    **{'data-component': '', 'type': 'hidden'})
            for i, item in enumerate(form.helper.layout):
                if type(item) == utils_forms.Submit:
                    form.helper.layout.pop(i)
                    break
            form.helper.layout.append(utils_forms.Submit(
                '<i class="sg sg-2x sg-camera"></i>', 'gallery-create', 'btn btn-backdrop btn-ts'))
            form.initial['pinned'] = True
            form.initial['public'] = True
            form.initial['text'] = 'Introgalerie der Gruppe @{}'.format(self.get_group().slug)
            form.initial['title'] = self.get_group()
            return form
        return None

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


class GroupAvatarUpdate(utils_views.ActionMixin, generic.UpdateView):
    action = 'Avatar ändern'
    fields = ('avatar',)
    layout = ('avatar',)
    menu = 'group'
    model = groups.Group
    permission_required = 'groups.change_group'

    def get_parent(self):
        return self.object


class GroupLogoUpdate(utils_views.ActionMixin, generic.UpdateView):
    action = 'Logo ändern'
    fields = ('logo',)
    layout = ('logo',)
    menu = 'group'
    model = groups.Group
    permission_required = 'groups.change_group'

    def get_parent(self):
        return self.object


class GroupMessages(utils_views.List):
    menu = 'group'
    permission_required = 'content.view_content_list'
    sidebar = []
    template_name = 'content/_thread_list.html'
    title = 'Gespräche'

    def get_queryset(self):
        return self.get_group().get_conversations(self.request.user)

    def get_parent(self):
        return self.get_group()

    def get_related_object(self):
        return self.get_group()


class Imprint(utils_views.PageMixin, generic.TemplateView):
    permission_required = 'entities.view_imprint'
    template_name = 'entities/imprint.html'
    title = 'Impressum'


class Privacy(utils_views.PageMixin, generic.TemplateView):
    permission_required = 'entities.view_imprint'
    template_name = 'entities/privacy.html'
    title = 'Datenschutz'
