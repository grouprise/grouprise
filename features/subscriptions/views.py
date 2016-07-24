from . import models
from django.contrib.contenttypes import models as contenttypes_models
from utils import forms, views


class SubscriptionMixin:
    model = models.Subscription
    title = 'Abonnement'


class Subscribe(SubscriptionMixin, views.Create):
    action = 'Abonnieren'
    fields = (
            forms.Field('content_type', type='constant'),
            forms.Field('object_id', type='constant'),
            forms.Field('subscriber', type='constant'))

    def get_initial(self):
        return {
                'content_type':
                contenttypes_models.ContentType.objects
                .get_for_model(self.related_object).pk,

                'object_id':
                self.related_object.pk,

                'subscriber':
                self.request.user.gestalt.pk,
                }


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
