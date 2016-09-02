from core import notifications
from entities import models


class ContentAssociated(notifications.Notification):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.association = kwargs['association']
        self.content = self.association.content

    def get_recipients(self):
        recipients = {self.content.author}
        if type(self.association) == models.GestaltContent:
            recipients.add(self.association.gestalt)
        if type(self.association) == models.GroupContent:
            recipients.update(models.Gestalt.objects.filter(
                memberships__group=self.association.group))
        recipients.discard(self.content.author)
        return recipients

    def get_sender(self):
        return self.content.author

    def get_subject(self):
        prefix = ''
        if type(self.association) == models.GroupContent:
            prefix = '[{}] '.format(self.association.group.slug)
        return prefix + self.content.title
