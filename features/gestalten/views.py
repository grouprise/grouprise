from django.core.urlresolvers import reverse
from django.views import generic

from . import models
from content import views as content_views
from core.views import base
from utils import views as utils_views


class List(base.PermissionMixin, generic.ListView):
    permission_required = 'gestalten.view_list'
    queryset = models.Gestalt.objects.filter(public=True).order_by('-score')
    template_name = 'gestalten/list.html'
    paginate_by = 10


class CalendarFeed(content_views.BaseCalendarFeed):

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
