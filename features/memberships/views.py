from . import models
from core import fields, views
from django import db, http, shortcuts
from django.contrib import messages
from django.core import urlresolvers
from features.gestalten import models as gestalten_models, views as gestalten_views
from features.groups import models as groups_models, views as groups_views
from utils import views as utils_views


class MembershipMixin(groups_views.Mixin):
    model = models.Membership
    title = 'Mitgliedschaft'

    def get_related_object(self):
        return self.get_group()


class Join(MembershipMixin, views.Create):
    action = 'Beitreten *'
    data_field_classes = (
            fields.current_gestalt('created_by'),
            fields.related_object('group'),
            fields.current_gestalt('member'))
    description = (
            'Der Gruppe <em>{{ group }}</em> auf {{ site.name }} beitreten *')
    permission = 'memberships.join_group'
    template_name = 'memberships/join.html'


class Members(gestalten_views.List):
    permission_required = 'memberships.view_list'
    template_name = 'memberships/list.html'

    def get_permission_object(self):
        self.group = shortcuts.get_object_or_404(
                groups_models.Group, pk=self.kwargs['group_pk'])
        return self.group

    def get_queryset(self):
        return gestalten_models.Gestalt.objects.filter(
                memberships__group=self.group).order_by('-score')


class MemberAdd(MembershipMixin, views.Create):
    action = 'Mitglied aufnehmen'
    data_field_classes = (
            fields.current_gestalt('created_by'),
            fields.related_object('group'),
            fields.email_gestalt('member'))
    permission = 'memberships.create_membership'

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except db.IntegrityError:
            messages.info(
                    self.request, 'Die Gestalt ist bereits Mitglied.')
            return http.HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return urlresolvers.reverse('members', args=(self.related_object.pk,))


class GestaltMemberAdd(utils_views.GestaltMixin, MemberAdd):
    data_field_classes = (
            fields.current_gestalt('created_by'),
            fields.related_object('group'),
            fields.view_object('member', key='gestalt'))
    description = (
            '<em>{{ gestalt }}</em> als Mitglied der Gruppe '
            '<em>{{ group }}</em> aufnehmen')
    permission = 'associations.create_content_group_membership'

    def get_permission_object(self):
        return self.related_object, self.get_gestalt()

    def get_view_object(self, key):
        if key == 'gestalt':
            return self.get_gestalt()
        return super().get_view_object(key)


class Resign(MembershipMixin, utils_views.Delete):
    action = 'Austreten'
    description = 'Aus der Gruppe <em>{{ group }}</em> austreten'
    permission = 'memberships.delete_membership'

    def get_object(self):
        return models.Membership.objects.filter(
                group=self.related_object,
                member=self.request.user.gestalt
                ).first()
