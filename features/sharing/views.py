from . import notifications
from core import fields, views
from features.groups import views as groups


class ShareGroupMixin(groups.Mixin, views.Form):
    data_field_classes = (fields.email('recipient'),)

    def get_related_object(self):
        return self.get_group()


class GroupRecommend(ShareGroupMixin):
    action = 'Gruppe empfehlen'
    message = 'Die Empfehlung wurde versendet.'
    permission = 'sharing.recommend_group'
    title = 'Empfehlung'

    def form_valid(self, form):
        notifications.GroupRecommend(
                group=self.related_object,
                recipient_email=form.cleaned_data['recipient_email']
                ).send()
        return super().form_valid(form)


class MemberInvite(ShareGroupMixin):
    action = 'Als Mitglied einladen'
    message = 'Die Einladung wurde versendet.'
    permission = 'sharing.invite_member'
    title = 'Einladung'

    def form_valid(self, form):
        notifications.MemberInvite(
                group=self.related_object,
                recipient_email=form.cleaned_data['recipient_email']
                ).send()
        return super().form_valid(form)
