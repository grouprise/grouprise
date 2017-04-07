from . import filters, models
from core import fields, views
from django import db, http
from django.contrib import messages
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
    message = 'Du erhältst nun Benachrichtigungen.'

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except db.IntegrityError:
            messages.info(
                    self.request, 'Du erhältst bereits Benachrichtigungen.')
            return http.HttpResponseRedirect(self.get_success_url())


class ContentSubscribe(Subscribe):
    description = (
            'Benachrichtigt werden, wenn zum Beitrag <em>{{ content }}</em> '
            'neue Kommentare veröffentlicht werden')
    permission = 'subscriptions.create_content_subscription'

    def get_related_object(self):
        return self.get_content()


class GroupSubscribe(groups.Mixin, Subscribe):
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


class AllContentUnsubscribe(SubscriptionMixin, groups.Mixin, views.Create):
    permission = 'subscriptions.create_all_content_unsubscription'

    action = 'Abbestellen'
    description = (
            'Keine Benachrichtigungen mehr für Beiträge und Gespräche der Gruppe '
            '<em>{{ group }}</em> erhalten')
    message = 'Du erhältst nun keine Benachrichtigungen mehr.'

    data_field_classes = (
            fields.related_object('subscribed_to'),
            fields.current_gestalt('subscriber'),
            fields.constant('unsubscribe', value=True),
            fields.create_reference(
                'filters', kwargs={'filter_id': filters.all_content.filter_id}),
            )

    def get_related_object(self):
        return self.get_group()


class ExternalContentUnsubscribe(SubscriptionMixin, groups.Mixin, views.Create):
    permission = 'subscriptions.create_external_content_unsubscription'

    action = 'Abbestellen'
    description = (
            'Keine Benachrichtigungen mehr für Gespräche der Gruppe '
            '<em>{{ group }}</em> erhalten, deren Autor nicht Gruppenmitglied '
            'ist')
    message = 'Du erhältst nun keine Benachrichtigungen mehr.'

    data_field_classes = (
            fields.related_object('subscribed_to'),
            fields.current_gestalt('subscriber'),
            fields.constant('unsubscribe', value=True),
            fields.create_reference(
                'filters', kwargs={'filter_id': filters.initial_author_no_member.filter_id}),
            )

    def get_related_object(self):
        return self.get_group()
