from . import models
from core import views


class SubscriptionMixin:
    model = models.Subscription
    title = 'Abonnement'


class Subscribe(SubscriptionMixin, views.Create):
    action = 'Abonnieren'
    fields = (
            views.Field('content_type', type='constant'),
            views.Field('object_id', type='constant'),
            views.Field('subscriber', data='actor', type='constant'))

    def get_initial(self):
        initial = super().get_initial()
        initial.update({
            'content_type':
            self.related_object.content_type.pk,

            'object_id':
            self.related_object.pk,
            })
        return initial


class ContentSubscribe(Subscribe):
    description = (
            'Benachrichtigt werden, wenn zum Beitrag <em>{{ content }}</em> '
            'neue Kommentare veröffentlicht werden')
    permission = 'subscriptions.create_content_subscription'

    def get_related_object(self):
        return self.get_content()


class GroupSubscribe(Subscribe):
    description = (
            'Benachrichtigt werden, wenn in der Gruppe <em>{{ group }}</em> '
            'neue Beiträge veröffentlicht werden')
    permission = 'subscriptions.create_group_subscription'

    def get_related_object(self):
        return self.get_group()


class Unsubscribe(SubscriptionMixin, views.Delete):
    action = 'Abbestellen'
    permission = 'subscriptions.delete_subscription'

    def get_object(self):
        return models.Subscription.objects.filter(
                subscribed_to=self.related_object,
                subscriber=self.request.user.gestalt
                ).first()


class ContentUnsubscribe(Unsubscribe):
    description = (
            'Keine Benachrichtigungen mehr für den Beitrag '
            '<em>{{ content }}</em> erhalten')

    def get_related_object(self):
        return self.get_content()


class GroupUnsubscribe(Unsubscribe):
    description = (
            'Keine Benachrichtigungen mehr für die Gruppe '
            '<em>{{ group }}</em> erhalten')

    def get_related_object(self):
        return self.get_group()
