from core import notifications
from features.conversations import models as conversations
from features.contributions import models as contributions
from features.memberships import models as memberships


class Contributed(notifications.Notification):
    generate_reply_tokens = True

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

    def get_recipients(self):
        recipients = set(self.object.container.get_authors())
        recipients.update(set(self.object.container.get_associated_gestalten()))
        for group in self.object.container.get_associated_groups():
            recipients.update(set(group.members.all()))
        return recipients

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
