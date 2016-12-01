from core.views import base
from django import shortcuts
from django.views import generic
from features.associations import models as associations


class Conversation(base.PermissionMixin, generic.DetailView):
    model = associations.Association
    permission = 'conversations.view'
    pk_url_kwarg = 'association_pk'
    template_name = 'conversations/conversation.html'
