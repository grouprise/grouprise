from core import views
from django import shortcuts
from features.associations import models as associations


class Conversation(views.List):
    template_name = 'conversations/conversation.html'
    permission = 'conversations.view'

    def get(self, *args, **kwargs):
        self.association = shortcuts.get_object_or_404(
                associations.Association, pk=self.kwargs['association_pk'])
        return super().get(*args, **kwargs)

    def get_queryset(self):
        return self.association.container.texts
