from core import notifications
from features.gestalten import models as gestalten


class Created(notifications.Notification):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = kwargs['text']

    def get_message_id(self):
        return self.text.get_unique_id()

    def get_recipients(self):
        recipients = set(self.text.container.get_authors())
        for group in self.text.container.get_groups():
            recipients.update(set(gestalten.Gestalt.objects.filter(
                memberships__group=group)))
        recipients.discard(self.text.author)
        return recipients

    def get_sender(self):
        return self.text.author

    def get_subject(self):
        prefix = '' if self.text.container.texts.first() == self.text else 'Re: '
        slugs = self.text.container.get_groups().values_list('slug', flat=True)
        groups = '[{}] '.format(','.join(slugs)) if slugs else ''
        return prefix + groups + self.text.container.subject
