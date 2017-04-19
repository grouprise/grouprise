from django.core.urlresolvers import reverse
from django.views import generic

from core.views import base
from utils import views as utils_views
import features.groups.models
import features.groups.views
from features.memberships.rules import is_member_of
from content import models, views as content_views


class List(base.PermissionMixin, generic.ListView):
    permission_required = 'events.view_list'
    template_name = 'events/list.html'
    paginate_by = 10

    def get_queryset(self):
        return models.Event.objects.can_view(self.request.user).upcoming()


class GroupCalendarFeed(content_views.BaseCalendarFeed, features.groups.views.Mixin):

    def items(self):
        filter_dict = {'groups': self.get_group(),
                       'public': (self.kwargs['domain'] == "public")}
        return super().items().filter(**filter_dict)

    def get_calendar_owner(self):
        return self.get_group()

    def check_authorization(self, authenticated_gestalt):
        return ((authenticated_gestalt is not None)
                and is_member_of(authenticated_gestalt.user, self.get_group()))


class CalendarExport(utils_views.PageMixin, generic.DetailView):
    sidebar = tuple()
    template_name = 'events/export.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['public_export_url'] = self.request.build_absolute_uri(
            reverse(self.feed_route, kwargs={
                self.slug_url_kwarg: self.get_object().slug,
                'domain': 'public'
            })
        )
        if self.has_private_access():
            relative_url = reverse(self.feed_route,
                                   kwargs={self.slug_url_kwarg: self.get_object().slug,
                                           'domain': 'private'})
            user_resolver = content_views.BaseCalendarFeed.user_resolver
            url_with_token = user_resolver.get_url_with_permission_token(
                self.get_object(), self.request.user.gestalt, relative_url)
            context['private_export_url'] = self.request.build_absolute_uri(url_with_token)
        return context


class GroupCalendarExport(CalendarExport):
    model = features.groups.models.Group
    slug_url_kwarg = 'group_slug'
    permission = 'entities.view_group'
    title = 'Exportmöglichkeiten für Gruppenkalender'
    parent = 'group'
    feed_route = 'group-events-feed'

    def get_parent(self):
        return self.get_group()

    def has_private_access(self):
        if self.request.user and self.request.user.is_authenticated():
            return is_member_of(self.request.user, self.get_group())
        else:
            return False
