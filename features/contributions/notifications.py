import os

import django

from core import notifications
from features.contributions import models as contributions
from features.memberships import models as memberships
from features.subscriptions.notifications import update_recipients


class ContributionCreated(notifications.Notification):
    @classmethod
    def get_recipients(cls, contribution):
        recipients = {}
        # send notifications to gestalten and groups associated with content (instance)
        for association in contribution.container.associations.all():
            if association.entity.is_group:
                # subscribed members receive a notification
                subscriptions = association.entity.subscriptions.filter(
                        subscriber__memberships__group=association.entity)
                update_recipients(
                        recipients, association=association, subscriptions=subscriptions)
            else:
                # associated gestalten receive a notification
                update_recipients(recipients, association=association)
        # send notifications to contributing gestalten
        update_recipients(recipients, contributions=contribution.container.contributions.all())
        return recipients

    def get_attachments(self):
        return [
            os.path.join(django.conf.settings.MEDIA_ROOT, c.contribution.file.name)
            for c in self.object.attachments.all()]

    def get_context_data(self, **kwargs):
        if type(self.object.contribution) == contributions.Text:
            kwargs['text'] = self.object.contribution.text
        elif type(self.object.contribution) == memberships.Application:
            kwargs['text'] = 'Ich beantrage die Mitgliedschaft in der Gruppe {}.'.format(
                    self.object.contribution.group)
        return super().get_context_data(**kwargs)

    def get_message_ids(self):
        my_id = self.object.get_unique_id()
        previous_texts = self.object.container.contributions.exclude(
                id=self.object.id)
        thread_obj = previous_texts.first()
        parent_obj = previous_texts.last()
        parent_id = parent_obj.get_unique_id() if parent_obj else None
        ref_ids = []
        if thread_obj:
            thread_id = thread_obj.get_unique_id()
            if thread_id != parent_id:
                ref_ids.append(thread_id)
        return my_id, parent_id, ref_ids

    def get_reply_token(self):
        return self.create_token()

    def get_sender(self):
        return self.object.author

    def get_subject(self):
        return self.object.container.subject

    def get_template_name(self):
        if self.object.container.is_conversation:
            name = 'conversations/contributed.txt'
        else:
            name = 'content/contributed.txt'
        return name

    def is_reply(self):
        return not (self.object.container.is_conversation
                    and self.object.container.contributions.first() == self.object)
