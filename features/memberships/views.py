from . import models
from django.core import urlresolvers
from entities import models as entities_models, views as entities_views
from utils import forms, views


class MembershipMixin:
    model = models.Membership
    title = 'Mitgliedschaft'

    def get_related_object(self):
        return self.get_group()


class Join(MembershipMixin, views.Create):
    action = 'Beitreten'
    description = (
            'Der Gruppe <em>{{ group }}</em> auf {{ site.name }} beitreten')
    fields = (
            forms.Field('group', type='constant'),
            forms.Field('member', type='constant'),)
    permission = 'memberships.join_group'

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
    fields = (
            forms.Field('group', type='constant'),
            forms.Field('member'))
    permission = 'memberships.create_membership'

    def get_initial(self):
        return {'group': self.related_object.pk}

    def get_success_url(self):
        return urlresolvers.reverse('members', args=(self.related_object.pk,))


class Resign(MembershipMixin, views.Delete):
    action = 'Austreten'
    description = 'Aus der Gruppe <em>{{ group }}</em> austreten'
    permission = 'memberships.delete_membership'

    def get_object(self):
        return models.Membership.objects.get(
                group=self.related_object,
                member=self.request.user.gestalt)
