from core import notifications
from entities import models
from features.gestalten import models as gestalten
from features.comments import notifications as comments


class Commented(comments.Commented):
    def get_recipients(self):
        recipients = super().get_recipients()
        recipients.update(self.comment.content.gestalten.all())
        for group in self.comment.content.groups.all():
            recipients.update(
                gestalten.Gestalt.objects.filter(memberships__group=group))
        recipients.discard(self.comment.author)
        return recipients


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
            recipients.update(gestalten.Gestalt.objects.filter(
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

    def get_message_id(self):
        return '{}.{}'.format(self.content.get_unique_id(), self.association.get_unique_id())
