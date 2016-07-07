from . import models
from django.contrib.contenttypes import models as contenttypes_models
from utils import views


class Subscribe(views.Create):
    action = 'Abonnieren'
    description = (
            'Benachrichtigt werden, wenn zum Beitrag <em>{{ content }}</em> '
            'neue Kommentare veröffentlicht werden')
    fields = ('content_type', 'object_id', 'subscriber',)
    model = models.Subscription
    title = 'Abonnement'

    def get_initial(self):
        return {
                'content_type': contenttypes_models.ContentType.objects \
                        .get_for_model(self.related_object),
                'object_id': self.related_object.pk,
                'subscriber': self.request.user.gestalt.pk,
                }


class ContentSubscribe(Subscribe):
    permission = 'subscriptions.create_content_subscription'

    def get_related_object(self):
        return self.get_content()


class Unsubscribe(views.Delete):
    model = models.Subscription
    permission = 'subscriptions.delete_subscription'

    def get_parent(self):
        return self.object.subscribed_to


class ContentUnsubscribe(Unsubscribe):
    def get_object(self):
        return models.Subscription.objects.filter(
                subscribed_to=self.get_content(),
                subscriber=self.request.user.gestalt
                ).first()


'''
class AttentionDelete(utils_views.ActionMixin, utils_views.DeleteView):
    action = 'Keine Benachrichtigungen mehr erhalten'
    layout = layout.HTML('<p>Möchtest Du wirklich keine Benachrichtigungen '
            'für den Beitrag <em>{{ attention.attended_object }}</em> mehr erhalten?</p>')
    permission = 'entities.delete_attention'

    def get_menu(self):
        return self.get_parent().get_type_name()

    def get_object(self):
        if 'content_pk' in self.request.resolver_match.kwargs:
            content = shortcuts.get_object_or_404(content_models.Content, pk=self.request.resolver_match.kwargs['content_pk'])
            return content.attentions.get(attendee=self.request.user.gestalt)

    def get_parent(self):
        return self.object.attended_object



class GroupAttentionCreate(utils_views.ActionMixin, generic.CreateView):
    action = 'Benachrichtigungen erhalten'
    form_class = forms.GroupAttention
    menu = 'group'
    permission = 'entities.create_group_attention'

    def get_initial(self):
        return {'attendee_email': self.request.user.email, 'group': self.get_group().pk}

    def get_parent(self):
        return self.get_group()

    def get_permission_object(self):
        return self.get_group()

class GroupAttentionDelete(utils_views.ActionMixin, utils_views.DeleteView):
    action = 'Keine Benachrichtigungen mehr erhalten'
    layout = layout.HTML('<p>Möchtest Du wirklich keine Benachrichtigungen '
            'für die Gruppe <em>{{ group }}</em> mehr erhalten?</p>')
    menu = 'group'
    model = subscriptions_models.Subscription
    permission = 'entities.delete_group_attention'

    def get_parent(self):
        return self.get_group()
'''
