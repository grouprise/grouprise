import django.views.generic
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.views import generic

import core.views
from utils import views as utils_views
from features.associations import models as associations
from features.content import models as content
from features.groups import models as groups
from features.memberships.rules import is_member_of
from content import models, views as content_views


class List(core.views.PermissionMixin, django.views.generic.ListView):
    permission_required = 'events.view_list'
    model = associations.Association
    template_name = 'events/list.html'
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().filter(
                container_type=content.Content.get_content_type(), content__time__isnull=False,
                ).can_view(self.request.user).order_by('-content__versions__time_created')


class CalendarFeed(content_views.BaseCalendarFeed):
    def items(self):
        filter_dict = {}
        # pick only events of the specified group
        group = models.Group.objects.get(slug=self.kwargs['group_slug'])
        filter_dict['groups'] = group
        domain = self.kwargs['domain']
        if domain == 'public':
            filter_dict['public'] = True
        else:
            self.authenticate()
            if not is_member_of(self.request.user, group):
                raise PermissionDenied
            filter_dict['public'] = False
        return super().items().filter(**filter_dict)


class CalendarExport(utils_views.PageMixin, generic.DetailView):
    model = groups.Group
    slug_url_kwarg = 'group_slug'
    sidebar = tuple()
    permission = 'entities.view_group'
    title = 'Exportmöglichkeiten für Gruppenkalender'
    template_name = 'groups/events_export.html'
    parent = 'group'

    def get_parent(self):
        return self.get_group()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['public_export_url'] = self.request.build_absolute_uri(
            reverse('group-events-feed', kwargs={
                'group_slug': self.get_object().slug,
                'domain': 'public'
            })
        )
        context['private_export_url'] = self.request.build_absolute_uri(
            reverse('group-events-feed', kwargs={
                'group_slug': self.get_object().slug,
                'domain': 'private'
            })
        )
        return context
