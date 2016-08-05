from . import models
from core import fields, views
from django import db, http
from django.contrib import messages
from django.core import urlresolvers
from entities import models as entities_models, views as entities_views
from features.groups import views as groups
from utils import forms, views as utils_views


class MembershipMixin(groups.GroupMixin):
    model = models.Membership
    title = 'Mitgliedschaft'

    def get_related_object(self):
        return self.get_group()


class Join(MembershipMixin, utils_views.Create):
    action = 'Beitreten *'
    description = (
            'Der Gruppe <em>{{ group }}</em> auf {{ site.name }} beitreten *')
    fields = (
            forms.Field('group', type='constant'),
            forms.Field('member', type='constant'),)
    permission = 'memberships.join_group'
    template_name = 'memberships/join.html'

    def get_initial(self):
        return {
                'group': self.related_object.pk,
                'member': self.request.user.gestalt.pk,
                }


class Members(MembershipMixin, entities_views.GestaltList):
    menu = 'group'
    permission = 'memberships.list_memberships'
    related_object_mandatory = True
    template_name = 'memberships/gestalt_list.html'
    title = 'Mitglieder'

    def get_parent(self):
        return self.related_object

    def get_queryset(self):
        return entities_models.Gestalt.objects.filter(
                membership__group=self.related_object)


class MemberCreate(MembershipMixin, views.Create):
    action = 'Mitglied aufnehmen'
    data_field_classes = (
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


class Resign(MembershipMixin, utils_views.Delete):
    action = 'Austreten'
    description = 'Aus der Gruppe <em>{{ group }}</em> austreten'
    permission = 'memberships.delete_membership'

    def get_object(self):
        return models.Membership.objects.filter(
                group=self.related_object,
                member=self.request.user.gestalt
                ).first()
