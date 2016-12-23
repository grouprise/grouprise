from . import forms
from core.views import base
from django import shortcuts
from django.contrib.messages import views as messages
from django.core import urlresolvers
from django.views import generic
from django.views.generic import edit
from features.associations import models as associations
from features.groups import models as groups
from features.texts import models as texts


class Conversation(base.PermissionMixin, edit.FormMixin, generic.DetailView):
    model = associations.Association
    pk_url_kwarg = 'association_pk'
    template_name = 'conversations/detail.html'

    form_class = forms.Reply

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_form_kwargs(self):
        text = texts.Text(author=self.request.user.gestalt, container=self.object.container)
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = text
        return kwargs

    def get_success_url(self):
        return urlresolvers.reverse('conversation', args=[self.object.pk])

    def has_permission(self):
        self.object = self.get_object()
        if self.request.method == 'GET':
            return self.request.user.has_perms(('conversations.view',), self.object)
        elif self.request.method == 'POST':
            return self.request.user.has_perms(('conversations.reply',), self.object)
        else:
            return False

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class Conversations(base.PermissionMixin, generic.ListView):
    model = associations.Association
    permission_required = 'conversations.list'
    template_name = 'conversations/list.html'
    paginate_by = 10

    def get(self, *args, **kwargs):
        self.group = shortcuts.get_object_or_404(groups.Group, pk=kwargs['group_pk'])
        return super().get(*args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().ordered_group_conversations(
                self.request.user, self.group)


class GroupConversations(Conversations):
    pass


class CreateConversation(
        base.PermissionMixin, messages.SuccessMessageMixin, generic.CreateView):
    model = associations.Association
    permission_required = 'conversations.create'
    template_name = 'conversations/create.html'

    form_class = forms.Create

    def get(self, *args, **kwargs):
        self.group = shortcuts.get_object_or_404(groups.Group, pk=kwargs['group_pk'])
        return super().get(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['has_author'] = self.request.user.is_authenticated()
        kwargs['instance'] = associations.Association(entity=self.group)
        kwargs['text'] = texts.Text()
        if kwargs['has_author']:
            kwargs['text'].author = self.request.user.gestalt
        return kwargs

    def get_success_message(self, cleaned_data):
        if self.request.user.is_authenticated():
            return None
        else:
            return 'Die Nachricht wurde versendet.'

    def get_success_url(self):
        if self.request.user.is_authenticated():
            return urlresolvers.reverse('conversation', args=[self.object.pk])
        else:
            return self.group.get_absolute_url()

    def post(self, *args, **kwargs):
        self.group = shortcuts.get_object_or_404(groups.Group, pk=kwargs['group_pk'])
        return super().post(*args, **kwargs)


class CreateGestaltConversation(CreateConversation):
    pass


class CreateGroupConversation(CreateConversation):
    pass
