from . import forms
from core.views import base
from django import http, shortcuts
from django.core import urlresolvers
from django.views import generic
from django.views.generic import edit
from features.associations import models as associations
from features.groups import models as groups
from features.texts import models as texts


class Conversation(base.PermissionMixin, edit.FormMixin, generic.DetailView):
    model = associations.Association
    permission_required = 'conversations.view'
    pk_url_kwarg = 'association_pk'
    template_name = 'conversations/detail.html'

    form_class = forms.Reply

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        text = texts.Text(author=self.request.user.gestalt, container=self.object.container)
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = text
        return kwargs

    def get_success_url(self):
        return urlresolvers.reverse('conversation', args=[self.object.pk])

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class CreateConversation(base.PermissionMixin, generic.CreateView):
    model = associations.Association
    permission_required = 'conversations.create'
    template_name = 'conversations/create.html'

    form_class = forms.Create

    def get(self, *args, **kwargs):
        self.group = shortcuts.get_object_or_404(groups.Group, pk=kwargs['group_pk'])
        return super().get(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = associations.Association(entity=self.group)
        kwargs['text'] = texts.Text(author=self.request.user.gestalt)
        return kwargs

    def get_success_url(self):
        return urlresolvers.reverse('conversation', args=[self.object.pk])

    def post(self, *args, **kwargs):
        self.group = shortcuts.get_object_or_404(groups.Group, pk=kwargs['group_pk'])
        return super().post(*args, **kwargs)
