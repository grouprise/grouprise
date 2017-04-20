from django import shortcuts
from django.conf import settings
from django.contrib.contenttypes import models as contenttypes
from django.contrib.messages import views as messages
from django.core import urlresolvers
from django.views import generic

import core.views
import features.contributions.models
import features.contributions.views
from . import forms
from features.gestalten import models as gestalten
from features.associations import models as associations
from features.groups import models as groups


class Conversation(
        features.contributions.views.ContributionFormMixin,
        core.views.PermissionMixin,
        generic.DetailView):

    permission_required = 'conversations.view'
    permission_required_post = 'conversations.reply'
    model = associations.Association
    pk_url_kwarg = 'association_pk'
    template_name = 'conversations/detail.html'

    form_class = forms.Reply


class Conversations(core.views.PermissionMixin, generic.ListView):
    model = associations.Association
    permission_required = 'conversations.list'
    template_name = 'conversations/list.html'
    paginate_by = 10

    def get_content(self):
        return associations.Association.objects.can_view(self.request.user)

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
        core.views.PermissionMixin, messages.SuccessMessageMixin, generic.CreateView):
    model = associations.Association
    template_name = 'conversations/create.html'

    form_class = forms.Create

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['has_author'] = self.request.user.is_authenticated()
        kwargs['instance'] = associations.Association(entity=self.entity)
        kwargs['contribution'] = features.contributions.models.Contribution()
        if kwargs['has_author']:
            kwargs['contribution'].author = self.request.user.gestalt
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
