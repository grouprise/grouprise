import datetime

import django.utils.timezone
import django.views.generic
from django.contrib.sites import models as sites_models
from django.contrib.sites.models import Site
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django_ical.views import ICalFeed
from django.utils.translation import gettext as _

import grouprise.core.views
import grouprise.features.content.views
import grouprise.features.groups.views
from grouprise.features.associations import models as associations
from grouprise.features.gestalten import models as gestalten
from grouprise.features.gestalten.auth.resolvers import get_user_resolver
from grouprise.features.groups.models import Group
from grouprise.features.memberships.predicates import is_member_of
from .utils import get_requested_time
from . import forms, models


class List(grouprise.core.views.PermissionMixin, django.views.generic.ListView):
    permission_required = 'events.view_list'
    model = associations.Association
    template_name = 'events/list.html'
    paginate_by = 10

    def get_content(self):
        return associations.Association.objects.can_view(self.request.user)

    def get_queryset(self):
        return super().get_queryset()\
            .filter_events()\
            .filter_upcoming(get_requested_time(self.request))\
            .can_view(self.request.user)\
            .order_by('content__time')


class Create(grouprise.features.content.views.Create):
    form_class = forms.EventCreateForm
    template_name = 'content/create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['with_time'] = True
        return kwargs


class Day(List):
    permission_required = 'events.view_day'

    def get_date(self):
        return django.views.generic.dates._date_from_string(
                self.kwargs['year'], '%Y',
                self.kwargs['month'], '%m',
                self.kwargs['day'], '%d')

    def get_queryset(self):
        date = self.get_date()
        return associations.Association.objects.filter_events().filter(
                content__time__gte=datetime.datetime.combine(date, datetime.time.min),
                content__time__lt=datetime.datetime.combine(
                    date + datetime.timedelta(days=1), datetime.time.min)
                ).can_view(self.request.user).order_by('content__time')


class Attendance(grouprise.core.views.PermissionMixin,
                 grouprise.features.associations.views.AssociationMixin,
                 django.views.generic.View):
    # TODO: remove the GET request as soon as we emit a real DELETE request via javascript
    http_method_names = ['get', 'delete', 'post']
    permission_required = 'events.can_change_attendance'

    def get_association(self):
        association_pk = self.kwargs.get('association_pk')
        return django.shortcuts.get_object_or_404(associations.Association, pk=association_pk)

    def get_permission_object(self):
        return self.get_association()

    def get_success_redirect(self):
        association = self.get_association()
        request = self.request
        if request.method == 'GET':
            redirect_url = request.GET.get('redirect_url')
        elif request.method == 'POST':
            redirect_url = request.POST.get('redirect_url')
        elif request.method == 'DELETE':
            redirect_url = request.DELETE.get('redirect_url')
        else:
            redirect_url = None
        if redirect_url is None:
            redirect_url = reverse('content-permalink', args=[association.pk])
        return HttpResponseRedirect(redirect_url)

    def get_attendee(self, request):
        if request.method == 'GET':
            other_pk = request.GET.get('other_gestalt')
        elif request.method == 'POST':
            other_pk = request.POST.get('other_gestalt')
        elif request.method == 'DELETE':
            other_pk = request.DELETE.get('other_gestalt')
        else:
            other_pk = None
        try:
            other_pk = int(other_pk)
        except ValueError:
            other_pk = None
        if other_pk is not None:
            return gestalten.Gestalt.objects.get(pk=other_pk)
        else:
            return request.user.gestalt

    def get_attendance_statement(self, request):
        gestalt = self.get_attendee(request)
        association = self.get_association()
        try:
            return models.AttendanceStatement.objects.filter(attendee=gestalt,
                                                             content=association.container).first()
        except models.AttendanceStatement.DoesNotExist:
            # we tolerate duplicate calls
            return None

    # TODO: remove the GET request as soon as we emit a real DELETE request via javascript
    def get(self, request, **kwargs):
        return self.delete(request, **kwargs)

    def delete(self, request, **kwargs):
        statement = self.get_attendance_statement(request)
        if statement is not None:
            statement.delete()
        return self.get_success_redirect()

    def post(self, request, **kwargs):
        statement = self.get_attendance_statement(request)
        if statement is None:
            gestalt = self.get_attendee(request)
            association = self.get_association()
            models.AttendanceStatement(attendee=gestalt, content=association.container).save()
        return self.get_success_redirect()


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
                return associations.Association.objects.filter_upcoming().filter(**filter_dict)
            else:
                # non-public items cannot be accessed without being authorized
                raise PermissionDenied
        else:
            return associations.Association.objects.filter_upcoming().can_view(user).filter(
                    **filter_dict)

    def assemble_content_filter_dict(self, filter_dict):
        filter_dict['public'] = (self.kwargs.get('domain', 'public') == 'public')

    def get_authorized_user(self):
        authenticated_gestalt = self.user_resolver.resolve_user(self.request,
                                                                self.get_calendar_owner())
        if authenticated_gestalt:
            if self.check_authorization(authenticated_gestalt):
                return authenticated_gestalt.user
        return None

    # the following methods describe ICAL properties
    # See http://django-ical.readthedocs.io/en/latest/usage.html#property-reference-and-extensions
    def product_id(self):
        return 'PRODID:-//{}//grouprise//DE'.format(Site.objects.get_current().domain)

    def timezone(self):
        return django.utils.timezone.get_default_timezone_name()

    def items(self):
        return self.get_queryset().order_by('-content__time')

    def item_class(self, item):
        if item.content.first().associations.first().public:
            return 'PUBLIC'
        else:
            return 'PRIVATE'

    def item_title(self, item):
        return item.content.first().title

    def item_description(self, item):
        return item.content.first().versions.last().text

    def item_location(self, item):
        return item.content.first().place

    def item_start_datetime(self, item):
        tz = django.utils.timezone.get_default_timezone()
        return item.content.first().time.astimezone(tz)

    def item_end_datetime(self, item):
        end_time = item.content.first().until_time
        if end_time is None:
            return None
        else:
            tz = django.utils.timezone.get_default_timezone()
            return end_time.astimezone(tz)


class GroupCalendarFeed(BaseCalendarFeed):

    def get_group(self):
        for attr in ('object', 'related_object'):
            if hasattr(self, attr):
                instance = getattr(self, attr)
                if isinstance(instance, Group):
                    return instance
                if hasattr(instance, 'group'):
                    return instance.group
                if hasattr(instance, 'groups'):
                    return instance.groups.first()
        try:
            if 'group_pk' in self.kwargs:
                return Group.objects.get(
                        pk=self.kwargs['group_pk'])
            if 'group_slug' in self.kwargs:
                return Group.objects.get(
                        slug=self.kwargs['group_slug'])
            if 'group' in self.request.GET:
                return Group.objects.get(
                        slug=self.request.GET['group'])
        except Group.DoesNotExist:
            pass
        return None

    def title(self):
        site_name = sites_models.Site.objects.get_current().name
        group = self.get_group()
        if group is None:
            return None
        else:
            return '{} ({})'.format(group.name, site_name)

    def items(self):
        filter_dict = {'group': self.get_group(),
                       'public': (self.kwargs['domain'] == "public")}
        return super().items().filter(**filter_dict)

    def item_guid(self, item):
        domain = sites_models.Site.objects.get_current().domain
        group = self.get_group()
        if group is None:
            return None
        else:
            return '{}.{}@{}'.format(group.name, item.id, domain)

    def get_calendar_owner(self):
        return self.get_group()

    def check_authorization(self, authenticated_gestalt):
        return ((authenticated_gestalt is not None)
                and is_member_of(authenticated_gestalt.user, self.get_group()))


class SiteCalendarFeed(BaseCalendarFeed):
    def get_calendar_owner(self):
        return None

    def item_title(self, item):
        entity = item.content.first().associations.first().entity
        if entity.is_group:
            return '[{}] {}'.format(entity.slug, item.content.first().title)
        else:
            return super().item_title(item)

    def title(self):
        return sites_models.Site.objects.get_current().name


class CalendarExport(generic.DetailView):
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
    model = grouprise.features.groups.models.Group
    slug_url_kwarg = 'group_slug'
    permission_required = 'groups.view'
    title = _("Export of group's calendars")
    parent = 'group'
    feed_route = 'group-events-feed'

    def get_parent(self):
        return self.get_group()

    def has_private_access(self):
        if self.request.user and self.request.user.is_authenticated:
            return is_member_of(self.request.user, self.object)
        else:
            return False


class SiteCalendarExport(generic.TemplateView):
    permission_required = 'stadt.view_index'
    title = _('Export of calendars')
    feed_route = 'site-events-feed'
    template_name = 'events/export.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['public_export_url'] = self.request.build_absolute_uri(
            reverse(self.feed_route))
        return context


class GestaltCalendarFeed(BaseCalendarFeed):

    def get_calendar_owner(self):
        return django.shortcuts.get_object_or_404(
                gestalten.Gestalt, user__username=self.kwargs.get('gestalt_slug'))

    def check_authorization(self, authenticated_gestalt):
        return authenticated_gestalt == self.get_calendar_owner()

    def assemble_content_filter_dict(self, filter_dict):
        filter_dict['gestalt'] = self.get_gestalt()
        super().assemble_content_filter_dict(filter_dict)


class GestaltCalendarExport(generic.DetailView):
    model = gestalten.Gestalt
    slug_url_kwarg = 'gestalt_slug'
    sidebar = tuple()
    permission = 'gestalten.view'
    title = _("Export of figure's calendars")
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
