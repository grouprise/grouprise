from . import models
from core import fields, views
from features.content import views as content
from features.groups import views as groups


class SubscriptionMixin:
    model = models.Subscription
    title = 'Abonnement'


class Subscribe(SubscriptionMixin, views.Create):
    action = 'Abonnieren'
    data_field_classes = (
            fields.related_object('subscribed_to'),
            fields.current_gestalt('subscriber'))


class ContentSubscribe(content.ContentMixin, Subscribe):
    description = (
            'Benachrichtigt werden, wenn zum Beitrag <em>{{ content }}</em> '
            'neue Kommentare veröffentlicht werden')
    permission = 'subscriptions.create_content_subscription'

    def get_related_object(self):
        return self.get_content()


class GroupSubscribe(groups.GroupMixin, Subscribe):
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
