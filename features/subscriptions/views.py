from . import models
from crispy_forms import layout
from django import forms as django_forms
from django.contrib.contenttypes import models as contenttypes_models
from utils import forms as utils_forms, views


class SubscriptionMixin:
    model = models.Subscription
    title = 'Abonnement'


class Subscribe(SubscriptionMixin, views.Create):
    action = 'Abonnieren'
    fields = (
            utils_forms.Field('content_type', type='constant'), 
            utils_forms.Field('object_id', type='constant'),
            utils_forms.Field('subscriber', type='constant'))

    def get_initial(self):
        return {
                'content_type': contenttypes_models.ContentType.objects \
                        .get_for_model(self.related_object).pk,
                'object_id': self.related_object.pk,
                'subscriber': self.request.user.gestalt.pk,
                }


class ContentSubscribe(Subscribe):
    description = (
            'Benachrichtigt werden, wenn zum Beitrag <em>{{ content }}</em> '
            'neue Kommentare veröffentlicht werden')
    permission = 'subscriptions.create_content_subscription'

    def get_related_object(self):
        return self.get_content()


class Unsubscribe(SubscriptionMixin, views.Delete):
    action = 'Abonnement aufheben'
    permission = 'subscriptions.delete_subscription'

    def get_parent(self):
        return self.object.subscribed_to


class ContentUnsubscribe(Unsubscribe):
    description = (
            'Keine Benachrichtigungen mehr für den Beitrag '
            '<em>{{ content }}</em> erhalten')

    def get_object(self):
        return models.Subscription.objects.filter(
                subscribed_to=self.get_content(),
                subscriber=self.request.user.gestalt
                ).first()


'''
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
