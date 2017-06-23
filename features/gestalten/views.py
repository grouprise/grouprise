import django
from django.core.urlresolvers import reverse
from django.views import generic

import utils
from utils import views as utils_views
from core.views import base
from features.associations import models as associations
from features.content import models as content
from features.events import views as events
from . import forms, models


class List(base.PermissionMixin, generic.ListView):
    permission_required = 'gestalten.view_list'
    queryset = models.Gestalt.objects.filter(public=True)
    ordering = '-score'
    paginate_by = 10
    template_name = 'gestalten/list.html'

    def get_content(self):
        return associations.Association.objects.filter(
                entity_type=models.Gestalt.get_content_type()).can_view(self.request.user)


class CalendarFeed(events.BaseCalendarFeed):

    def get_calendar_owner(self):
        return self.get_gestalt()

    def check_authorization(self, authenticated_gestalt):
        return authenticated_gestalt == self.get_calendar_owner()

    def assemble_content_filter_dict(self, filter_dict):
        filter_dict['gestalt'] = self.get_gestalt()
        super().assemble_content_filter_dict(filter_dict)


class CalendarExport(utils_views.PageMixin, generic.DetailView):
    model = models.Gestalt
    slug_url_kwarg = 'gestalt_slug'
    sidebar = tuple()
    permission = 'entities.view_gestalt'
    title = 'Exportmöglichkeiten für Gestaltenkalender'
    template_name = 'gestalten/events_export.html'
    parent = 'gestalt-index'

    def get_parent(self):
        return self.get_gestalt()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['public_export_url'] = self.request.build_absolute_uri(
            reverse('gestalt-events-feed', kwargs={
                'gestalt_slug': self.get_object().slug,
                'domain': 'public'
            })
        )
        context['private_export_url'] = self.request.build_absolute_uri(
            reverse('gestalt-events-feed', kwargs={
                'gestalt_slug': self.get_object().slug,
                'domain': 'private'
            })
        )
        return context


class GestaltUpdate(utils.views.ActionMixin, django.views.generic.UpdateView):
    action = 'Dein Profil'
    form_class = forms.Gestalt
    menu = 'gestalt'
    message = 'Die Einstellungen wurden geändert.'
    model = models.Gestalt
    permission_required = 'entities.change_gestalt'

    def get_parent(self):
        return self.object


class GestaltAvatarUpdate(utils.views.ActionMixin, django.views.generic.UpdateView):
    action = 'Avatar ändern'
    fields = ('avatar',)
    layout = ('avatar',)
    menu = 'gestalt'
    model = models.Gestalt
    permission_required = 'entities.change_gestalt'

    def get_parent(self):
        return self.object


class GestaltBackgroundUpdate(utils.views.ActionMixin, django.views.generic.UpdateView):
    action = 'Hintergrundbild ändern'
    fields = ('background',)
    layout = ('background',)
    menu = 'gestalt'
    model = models.Gestalt
    permission_required = 'entities.change_gestalt'

    def get_parent(self):
        return self.object


class Gestalt(utils_views.List):
    menu = 'gestalt'
    model = associations.Association
    permission_required = 'entities.view_gestalt'
    sidebar = ('calendar',)
    template_name = 'entities/gestalt_detail.html'

    def get(self, request, *args, **kwargs):
        if not self.get_gestalt():
            raise django.http.Http404('Gestalt nicht gefunden')
        return super().get(request, *args, **kwargs)

    def get_permission_object(self):
        return self.get_gestalt()

    def get_queryset(self):
        return super().get_queryset().filter(
                container_type=content.Content.content_type,
                entity_type=self.get_gestalt().get_content_type(),
                entity_id=self.get_gestalt().id
                ).can_view(self.request.user).annotate(time_created=django.db.models.Min(
                    'content__versions__time_created')).order_by('-time_created')

    def get_title(self):
        return str(self.get_gestalt())
