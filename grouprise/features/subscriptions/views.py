from django.db import IntegrityError
from django.contrib.messages import success, info
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, DeleteView, FormView

from grouprise.core.models import PermissionToken
from grouprise.core.views import PermissionMixin
from grouprise.features.gestalten.models import Gestalt
from grouprise.features.groups.models import Group
from grouprise.features.subscriptions.models import Subscription
from grouprise.features.subscriptions.rules import is_subscribed
from . import forms, notifications


class GroupSubscribe(SuccessMessageMixin, PermissionMixin, CreateView):
    permission_required = 'subscriptions.create'
    form_class = forms.Subscribe
    template_name = 'subscriptions/create.html'
    success_message = 'Du erhältst zukünftig Benachrichtigungen für Beiträge dieser Gruppe.'
    already_subscribed_message = 'Du hast diese Gruppe bereits abonniert.'

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except IntegrityError:
            info(self.request, self.already_subscribed_message)
            return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_instance()
        return kwargs

    def get_instance(self):
        instance = Subscription()
        if self.request.user.is_authenticated:
            instance.subscriber = self.request.user.gestalt
        instance.subscribed_to = self.group
        return instance

    def get_permission_object(self):
        self.group = get_object_or_404(Group, pk=self.kwargs.get('group_pk'))
        return self.group

    def get_success_url(self):
        return self.group.get_absolute_url()

    def handle_no_permission(self):
        if (self.request.user.is_authenticated
                and is_subscribed(self.request.user, self.group)):
            info(self.request, self.already_subscribed_message)
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super().handle_no_permission()


class GroupUnsubscribe(PermissionMixin, DeleteView):
    permission_required = 'subscriptions.delete'
    model = Subscription
    template_name = 'subscriptions/delete.html'

    def delete(self, *args, **kwargs):
        success(
                self.request,
                'Du erhältst zukünftig keine Benachrichtigungen mehr für Beiträge dieser '
                'Gruppe.')
        return super().delete(*args, **kwargs)

    def get_object(self):
        return self.gestalt.subscriptions.filter(
                subscribed_to_type=self.group.content_type, subscribed_to_id=self.group.id)

    def get_permission_object(self):
        self.gestalt = self.request.user.gestalt if self.request.user.is_authenticated else None
        self.group = get_object_or_404(Group, pk=self.kwargs.get('group_pk'))
        return self.group

    def get_success_url(self):
        return self.group.get_absolute_url()


class GroupUnsubscribeConfirm(GroupUnsubscribe):
    def delete(self, *args, **kwargs):
        self.token.delete()
        return super().delete(*args, **kwargs)

    def get_permission_object(self):
        self.token = get_object_or_404(
                PermissionToken, feature_key='group-unsubscribe',
                secret_key=self.kwargs.get('secret_key'))
        self.gestalt = self.token.gestalt
        self.group = self.token.target
        return self.group

    def has_permission(self):
        obj = self.get_permission_object()
        perms = self.get_permission_required()
        return self.gestalt.user.has_perms(perms, obj)


class GroupUnsubscribeRequest(PermissionMixin, FormView):
    permission_required = 'subscriptions.delete_request'
    form_class = forms.UnsubscribeRequest
    template_name = 'subscriptions/delete_request.html'

    def form_valid(self, form):
        email = form.cleaned_data['subscriber']
        try:
            subscriber = self.group.subscribers.get_by_email(email)
            notification = notifications.Subscriber(self.group)
            notification.token = PermissionToken.objects.create(
                    gestalt=subscriber, target=self.group, feature_key='group-unsubscribe')
            notification.send(subscriber)
        except Gestalt.DoesNotExist:
            notifications.NoSubscriber(self.group).send(email)
        info(self.request, 'Es wurde eine E-Mail an die angebene Adresse versendet.')
        return super().form_valid(form)

    def get_permission_object(self):
        self.group = get_object_or_404(Group, pk=self.kwargs.get('group_pk'))
        return self.group

    def get_success_url(self):
        return self.group.get_absolute_url()
