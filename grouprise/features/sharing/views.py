from django.views.generic import FormView

from grouprise.core.views import PermissionMixin
from . import notifications


# class ShareGroupMixin(groups.Mixin, views.Form):
#     data_field_classes = (fields.email('recipient'),)
#
#     def get_related_object(self):
#         return django.shortcuts.get_object_or_404(
#                 grouprise.features.groups.models.Group, pk=self.kwargs.get('group_pk'))


class GroupRecommend(PermissionMixin, FormView):
    action = 'Gruppe empfehlen'
    message = 'Die Empfehlung wurde versendet.'
    permission_required = 'sharing.recommend_group'
    title = 'Empfehlung'

    def form_valid(self, form):
        notifications.GroupRecommend(self.related_object).send(
                form.cleaned_data['recipient_email'])
        return super().form_valid(form)


class MemberInvite(PermissionMixin, FormView):
    action = 'Als Mitglied einladen'
    message = 'Die Einladung wurde versendet.'
    permission_required = 'sharing.invite_member'
    title = 'Einladung'

    def form_valid(self, form):
        notifications.MemberInvite(self.related_object).send(
                form.cleaned_data['recipient_email'])
        return super().form_valid(form)
