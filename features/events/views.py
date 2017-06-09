import datetime

import django.utils.timezone
import django.views.generic
from django.contrib.sites import models as sites_models
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views import generic
from django_ical.views import ICalFeed

import core.views
import features.content.views
import features.groups.views
from features.associations import models as associations
from features.memberships.predicates import is_member_of
from utils import views as utils_views
from utils.auth import get_user_resolver


class List(core.views.PermissionMixin, django.views.generic.ListView):
    permission_required = 'events.view_list'
    model = associations.Association
    template_name = 'events/list.html'
    paginate_by = 10

    def get_content(self):
        return associations.Association.objects.can_view(self.request.user)

    def get_queryset(self):
        return super().get_queryset().filter_events().filter_upcoming().can_view(
                self.request.user).order_by('content__time')


class Create(features.content.views.Create):
    template_name = 'events/create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['with_time'] = True
        return kwargs


class Day(List):
    permission_required = 'events.view_day'

    def get_date(self):
        return django.views.generic.dates._date_from_string(
                self.kwargs['year'], '%Y',
                self.kwargs['month'], '%b',
                self.kwargs['day'], '%d')

    def get_queryset(self):
        date = self.get_date()
        return associations.Association.objects.filter_events().filter(
                content__time__gte=datetime.datetime.combine(date, datetime.time.min),
                content__time__lt=datetime.datetime.combine(
                    date + datetime.timedelta(days=1), datetime.time.min)
                ).can_view(self.request.user).order_by('content__time')


class BaseCalendarFeed(ICalFeed):

    user_resolver = get_user_resolver("calendar")

    def __call__(self, request, *args, **kwargs):
        self.request = request
        self.kwargs = kwargs
        try:
            return super().__call__(request, *args, **kwargs)
        except PermissionDenied:
            response = HttpResponse()
            response.status_code = 401
            domain = sites_models.Site.objects.get_current().domain
            response['WWW-Authenticate'] = 'Basic realm="{}"'.format(domain)
            return response

    def get_queryset(self):
        user = self.get_authorized_user()
        filter_dict = {}
        self.assemble_content_filter_dict(filter_dict)
        if user is None:
            if filter_dict['public']:
                return associations.Association.objects.filter_events().filter(**filter_dict)
            else:
                # non-public items cannot be accessed without being authorized
                raise PermissionDenied
        else:
            return associations.Association.objects.filter_events().can_view(user).filter(
                    **filter_dict)

    def assemble_content_filter_dict(self, filter_dict):
        filter_dict['public'] = (self.kwargs['domain'] == 'public')

    def get_authorized_user(self):
        authenticated_gestalt = self.user_resolver.resolve_user(self.request,
                                                                self.get_calendar_owner())
        if authenticated_gestalt:
            if self.check_authorization(authenticated_gestalt):
                return authenticated_gestalt.user
        return None

    def items(self):
        return self.get_queryset().order_by('-content__time')

    def item_title(self, item):
        return item.content.first().title

    def item_description(self, item):
        return item.content.first().subject

    def item_location(self, item):
        return item.content.first().place

    def item_start_datetime(self, item):
        return item.content.first().time


class GroupCalendarFeed(BaseCalendarFeed, features.groups.views.Mixin):

    def items(self):
        filter_dict = {'group': self.get_group(),
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
            user_resolver = BaseCalendarFeed.user_resolver
            url_with_token = user_resolver.get_url_with_permission_token(
                self.get_object(), self.request.user.gestalt, relative_url)
            context['private_export_url'] = self.request.build_absolute_uri(url_with_token)
        return context


class GroupCalendarExport(CalendarExport):
    model = features.groups.models.Group
    slug_url_kwarg = 'group_slug'
    permission_required = 'entities.view_group'
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
