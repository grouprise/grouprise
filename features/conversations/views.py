from . import forms
from core.views import base
from django import shortcuts
from django.conf import settings
from django.contrib.contenttypes import models as contenttypes
from django.contrib.messages import views as messages
from django.core import urlresolvers
from django.views import generic
from django.views.generic import edit
from features.gestalten import models as gestalten
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

    def get_queryset(self):
        return super().get_queryset().ordered_conversations(self.request.user)


class GroupConversations(Conversations):
    permission_required = 'conversations.list_group'
    template_name = 'conversations/list_group.html'

    def get_permission_object(self):
        self.group = shortcuts.get_object_or_404(groups.Group, pk=self.kwargs['group_pk'])
        return self.group

    def get_queryset(self):
        return super().get_queryset().filter(
            entity_type=contenttypes.ContentType.objects.get_for_model(self.group),
            entity_id=self.group.id)


class CreateConversation(
        base.PermissionMixin, messages.SuccessMessageMixin, generic.CreateView):
    model = associations.Association
    template_name = 'conversations/create.html'

    form_class = forms.Create

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['has_author'] = self.request.user.is_authenticated()
        kwargs['instance'] = associations.Association(entity=self.entity)
        kwargs['text'] = texts.Text()
        if kwargs['has_author']:
            kwargs['text'].author = self.request.user.gestalt
        return kwargs

    def get_success_message(self, cleaned_data):
        if not self.request.user.is_authenticated():
            return 'Die Nachricht wurde versendet.'

    def get_success_url(self):
        if self.request.user.is_authenticated():
            return urlresolvers.reverse('conversation', args=[self.object.pk])
        else:
            return self.entity.get_absolute_url()


class CreateGestaltConversation(CreateConversation):
    permission_required = 'conversations.create_gestalt_conversation'

    def get(self, *args, **kwargs):
        self.entity = shortcuts.get_object_or_404(gestalten.Gestalt, pk=kwargs['gestalt_pk'])
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.entity = shortcuts.get_object_or_404(gestalten.Gestalt, pk=kwargs['gestalt_pk'])
        return super().post(*args, **kwargs)


class CreateGroupConversation(CreateConversation):
    permission_required = 'conversations.create_group_conversation'

    def get(self, *args, **kwargs):
        self.entity = shortcuts.get_object_or_404(groups.Group, pk=kwargs['group_pk'])
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.entity = shortcuts.get_object_or_404(groups.Group, pk=kwargs['group_pk'])
        return super().post(*args, **kwargs)


class CreateAbuseConversation(CreateGroupConversation):
    def get(self, *args, **kwargs):
        kwargs['group_pk'] = settings.ABOUT_GROUP_ID
        return super().get(*args, **kwargs)

    def get_initial(self):
        return {
                'subject': 'Missbrauch melden',
                'text': '{}\n\nIch bin der Ansicht, dass der Inhalt dieser Seite gegen '
                        'Regeln verstößt.'.format(
                            self.request.build_absolute_uri(self.kwargs['path']))}

    def post(self, *args, **kwargs):
        kwargs['group_pk'] = settings.ABOUT_GROUP_ID
        return super().post(*args, **kwargs)
