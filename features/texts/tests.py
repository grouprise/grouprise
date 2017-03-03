from . import models
from core import tests
from django.core import mail
from django_mailbox import models as mailbox_models, signals as mailbox_signals
from features.gestalten import tests as gestalten


class ReplyByEmail(gestalten.AuthenticatedMixin, gestalten.OtherGestaltMixin, tests.Test):
    def test_texts_reply_by_email(self):
        # send message to other_gestalt via web interface
        self.client.post(
                self.get_url('create-gestalt-conversation', self.other_gestalt.pk),
                {'subject': 'Subject A', 'text': 'Text A'})
        text_a = self.assertExists(models.Text, conversation__subject='Subject A')
        self.assertNotificationSent()
        # generate reply message
        reply_to = mail.outbox[0].extra_headers['Reply-To']
        msg = mailbox_models.Message(to_header=reply_to, body='Text B')
        # send signal like getmail would
        mailbox_signals.message_received.send(self, message=msg)
        self.assertExists(models.Text, conversation=text_a.conversation.get(), text='Text B')
