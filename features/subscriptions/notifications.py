import os

import django

from core import notifications
from features.conversations import models as conversations
from features.contributions import models as contributions
from features.memberships import models as memberships
from features.gestalten import models as gestalten
from features.groups.models import Group
import core.notifications


def update_recipients(recipients_dict, association=None, subscriptions=[], contributions=[]):
    # association für [betreff]
    # reason für --signatur
    # sender für From:
    # sender ist member?
    # content oder conversation?
    for subscription in subscriptions:
        recipients_dict[subscription.subscriber] = {}
    for contribution in contributions:
        recipients_dict[contribution.author] = {}
    if association and not association.entity.is_group:
        recipients_dict[association.entity] = {}


class ContentCreated(core.notifications.Notification):
    @classmethod
    def get_recipients(cls, content):
        recipients = {}
        # send notifications to groups associated with content (instance)
        associations = content.associations.filter(entity_type=Group.content_type)
        for association in associations:
            # all subscribers receive a notification
            subscriptions = association.entity.subscriptions.all()
            if not association.public:
                # for internal content, only subscribed members receive a notification
                subscriptions = subscriptions.filter(
                        subscriber__memberships__group=association.entity)
            update_recipients(recipients, association=association, subscriptions=subscriptions)
        return recipients

    def get_message_ids(self):
        return self.object.get_unique_id(), None, []

    def get_reply_token(self):
        return self.create_token()

    def get_sender(self):
        return self.object.versions.last().author

    def get_subject(self):
        #group = '[{}] '.format(self.object.entity.slug) if self.object.entity.is_group else ''
        return self.object.subject

    def get_template_name(self):
        if self.object.is_gallery:
            name = 'galleries/associated.txt'
        elif self.object.is_file:
            name = 'files/associated.txt'
        elif self.object.is_event:
            name = 'events/associated.txt'
        else:
            name = 'articles/associated.txt'
        return name


class ContributionCreated(notifications.Notification):
    generate_reply_tokens = True

    @classmethod
    def get_recipients(cls, contribution):
        recipients = {}
        # send notifications to gestalten and groups associated with content (instance)
        for association in contribution.container.associations:
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
        update_recipients(recipients, contributions=contribution.container.contributions)
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

    def get_sender(self):
        return self.object.author

    def get_subject(self):
        prefix = 'Re: '
        if (self.object.container_type == conversations.Conversation.get_content_type()
                and self.object.container.contributions.first() == self.object):
            prefix = ''
        slugs = self.object.container.get_associated_groups().values_list(
                'slug', flat=True)
        groups = '[{}] '.format(','.join(slugs)) if slugs else ''
        return prefix + groups + self.object.container.subject

    def get_template_name(self):
        if self.object.container.is_conversation:
            name = 'conversations/contributed.txt'
        else:
            name = 'content/contributed.txt'
        return name
