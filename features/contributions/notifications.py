from . import models
from core import notifications
from django import db
from django.conf import settings
from django.utils import crypto
from features.gestalten import models as gestalten


class Created(notifications.Notification):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = kwargs['contribution']

    def get_message_ids(self):
        my_id = self.text.get_unique_id()
        previous_texts = self.text.container.contributions.exclude(id=self.text.id)
        thread_obj = previous_texts.first()
        parent_obj = previous_texts.last()
        parent_id = parent_obj.get_unique_id() if parent_obj else None
        ref_ids = []
        if thread_obj:
            thread_id = thread_obj.get_unique_id()
            if thread_id != parent_id:
                ref_ids.append(thread_id)
        return my_id, parent_id, ref_ids

    def get_recipients(self):
        # find set of recipients
        recipients = set(self.text.container.get_authors())
        recipients.update(set(self.text.container.get_gestalten()))
        for group in self.text.container.get_groups():
            recipients.update(set(gestalten.Gestalt.objects.filter(
                memberships__group=group)))
        # assign a reply key to each recipient
        result = {}
        for gestalt in recipients:
            while True:
                try:
                    key = crypto.get_random_string(
                            length=15, allowed_chars='abcdefghijklmnopqrstuvwxyz0123456789')
                    models.ReplyKey.objects.create(gestalt=gestalt, key=key, contribution=self.text)
                    result[gestalt] = {'reply_key': key}
                    break
                except db.IntegrityError:
                    pass
        return result

    def get_sender(self):
        return self.text.author

    def get_sender_email(self):
        return settings.ANSWERABLE_FROM_EMAIL

    def get_subject(self):
        prefix = '' if self.text.container.contributions.first() == self.text else 'Re: '
        slugs = self.text.container.get_groups().values_list('slug', flat=True)
        groups = '[{}] '.format(','.join(slugs)) if slugs else ''
        return prefix + groups + self.text.container.subject
