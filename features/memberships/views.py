from . import models
from utils import forms, views


class MembershipMixin:
    model = models.Membership
    title = 'Mitgliedschaft'


class Join(MembershipMixin, views.Create):
    action = 'Beitreten'
    description = 'Der Gruppe <em>{{ group }}</em> auf {{ site.name }} beitreten'
    fields = (
            forms.Field('group', type='constant'),
            forms.Field('member', type='constant'),)
    permission = 'memberships.create_membership'

    def get_initial(self):
        return {
                'group': self.related_object.pk,
                'member': self.request.user.gestalt.pk,
                }

    def get_related_object(self):
        return self.get_group()
