from . import notifications
from core import fields, views
from features.groups import views as groups


class GroupRecommend(groups.Mixin, views.Form):
    action = 'Gruppe empfehlen'
    data_field_classes = (fields.email('recipient'),)
    message = 'Die Empfehlung wurde versendet.'
    permission = 'sharing.recommend_group'
    title = 'Empfehlung'

    def form_valid(self, form):
        notifications.GroupRecommend(
                group=self.related_object,
                recipient_email=form.cleaned_data['recipient_email']
                ).send()
        return super().form_valid(form)

    def get_related_object(self):
        return self.get_group()
