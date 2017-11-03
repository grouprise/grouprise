import django

import features
from core import fields, views
from features.groups import views as groups
from . import notifications


class ShareGroupMixin(groups.Mixin, views.Form):
    data_field_classes = (fields.email('recipient'),)

    def get_related_object(self):
        return django.shortcuts.get_object_or_404(
                features.groups.models.Group, pk=self.kwargs.get('group_pk'))


class GroupRecommend(ShareGroupMixin):
    action = 'Gruppe empfehlen'
    message = 'Die Empfehlung wurde versendet.'
    permission_required = 'sharing.recommend_group'
    title = 'Empfehlung'

    def form_valid(self, form):
        notifications.GroupRecommend(self.related_object).send(
                form.cleaned_data['recipient_email'])
        return super().form_valid(form)


class MemberInvite(ShareGroupMixin):
    action = 'Als Mitglied einladen'
    message = 'Die Einladung wurde versendet.'
    permission_required = 'sharing.invite_member'
    title = 'Einladung'

    def form_valid(self, form):
        notifications.MemberInvite(self.related_object).send(
                form.cleaned_data['recipient_email'])
        return super().form_valid(form)
