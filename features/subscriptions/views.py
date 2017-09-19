import django
from django import db, http
from django.contrib import messages

import features
from core import fields, views
from features.groups import views as groups
from . import models


class SubscriptionMixin:
    model = models.Subscription
    title = 'Abonnement'


class Subscribe(SubscriptionMixin, views.Create):
    action = 'Abonnieren'
    data_field_classes = (
            fields.related_object('subscribed_to'),
            fields.current_gestalt('subscriber'))
    message = 'Du erhältst nun Benachrichtigungen.'
    template_name = 'subscriptions/create.html'

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except db.IntegrityError:
            messages.info(
                    self.request, 'Du erhältst bereits Benachrichtigungen.')
            return http.HttpResponseRedirect(self.get_success_url())


class GroupSubscribe(groups.Mixin, Subscribe):
    permission_required = 'subscriptions.create'

    def get_related_object(self):
        return django.shortcuts.get_object_or_404(
                features.groups.models.Group, pk=self.kwargs.get('group_pk'))

    def handle_no_permission(self):
        if self.request.user.is_authenticated():
            django.contrib.messages.info(
                    self.request, 'Du erhältst bereits Nachrichten für diese Gruppe.')
            return django.http.HttpResponseRedirect(self.related_object.get_absolute_url())
        else:
            return super().handle_no_permission()


class Unsubscribe(SubscriptionMixin, views.Delete):
    action = 'Abbestellen'
    permission_required = 'subscriptions.delete'

    def get_object(self):
        return models.Subscription.objects.filter(
                subscribed_to_type=self.related_object.content_type,
                subscribed_to_id=self.related_object.id,
                subscriber=self.request.user.gestalt
                ).first()

    def get_permission_object(self):
        return self.related_object


class GroupUnsubscribe(Unsubscribe):
    description = (
            'Keine Benachrichtigungen mehr für die Gruppe '
            '<em>{{ group }}</em> erhalten')

    def get_related_object(self):
        return self.get_group()
