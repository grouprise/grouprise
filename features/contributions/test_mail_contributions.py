import contextlib
import tempfile
import os

from django.conf import settings
from django.core import mail
from django.urls import reverse
from django_mailbox import models as mailbox_models, signals as mailbox_signals

from core import tests
from features.associations import models as associations
from features.gestalten import tests as gestalten
from features.memberships import test_mixins as memberships
from . import models


@contextlib.contextmanager
def get_temporary_media_file(content=None, suffix=None):
    file_handle, filename = tempfile.mkstemp(dir=settings.MEDIA_ROOT, suffix=suffix)
    if content is not None:
        os.write(file_handle, content)
    os.close(file_handle)
    yield filename
    try:
        os.unlink(filename)
    except OSError:
        pass


class ContentReplyByEmail(
        memberships.AuthenticatedMemberMixin, tests.Test):
    def test_content_reply_by_email(self):
        # create article
        self.client.post(
                reverse('create-group-article', args=(self.group.slug,)),
                {'title': 'Test', 'text': 'Test'})
        a = self.assertExists(associations.Association, content__title='Test')
        self.assertNotificationSent()
        # generate reply message
        reply_to = mail.outbox[0].extra_headers['Reply-To']
        msg = mailbox_models.Message(
                from_header=self.gestalt.user.email,
                body='Delivered-To: {}\n\nText B'.format(reply_to))
        # send signal like getmail would
        mailbox_signals.message_received.send(self, message=msg)
        self.assertExists(
                models.Contribution, content=a.content.get(),
                text__text='Text B')


class ConversationInitiateByEmail(memberships.MemberMixin, tests.Test):
    def test_conversation_initiate_by_email(self):
        # generate initial message
        msg = mailbox_models.Message(
                from_header=self.gestalt.user.email,
                body='Delivered-To: {}@localhost\n\nText A'.format(self.group.slug))
        # send signal like getmail would
        mailbox_signals.message_received.send(self, message=msg)
        self.assertExists(
                models.Contribution, conversation__associations__group=self.group,
                text__text='Text A')

    def test_conversation_initiate_by_email_failing(self):
        # generate initial message
        msg = mailbox_models.Message(
                from_header=self.gestalt.user.email,
                body='Delivered-To: not-existing@localhost\n\nText A')
        # send signal like getmail would
        mailbox_signals.message_received.send(self, message=msg)
        self.assertEqual(len(mail.outbox), 1)


class ConversationReplyByEmail(
        gestalten.AuthenticatedMixin, gestalten.OtherGestaltMixin, tests.Test):
    def test_texts_reply_by_email(self):
        # send message to other_gestalt via web interface
        self.client.post(
                self.get_url('create-gestalt-conversation', self.other_gestalt.pk),
                {'subject': 'Subject A', 'text': 'Text A'})
        text_a = self.assertExists(models.Contribution, conversation__subject='Subject A')
        self.assertNotificationSent()
        # generate reply message
        reply_to = mail.outbox[0].extra_headers['Reply-To']
        msg = mailbox_models.Message(
                from_header=self.other_gestalt.user.email,
                body='Delivered-To: {}\n\nText B'.format(reply_to))
        # send signal like getmail would
        mailbox_signals.message_received.send(self, message=msg)
        self.assertExists(
                models.Contribution, conversation=text_a.conversation.get(),
                text__text='Text B')


class ConversationAttachments(memberships.MemberMixin, tests.Test):

    def test_conversation_initiate_with_attachments(self):
        with get_temporary_media_file(content=b"foo") as filename1, \
                get_temporary_media_file(content=b"bar") as filename2:
            box = mailbox_models.Mailbox.objects.create()
            msg = mailbox_models.Message.objects.create(
                    mailbox=box,
                    from_header=self.gestalt.user.email,
                    body='Delivered-To: {}@localhost\n\nText B'.format(self.group.slug),
            )
            mailbox_models.MessageAttachment.objects.create(
                message=msg, headers="Content-Type: text/plain",
                document=os.path.basename(filename1))
            # this file should be ignore (based on its content type)
            mailbox_models.MessageAttachment.objects.create(
                message=msg, headers="Content-Type: application/pgp-signature",
                document=os.path.basename(filename2))
            # send signal like getmail would
            mailbox_signals.message_received.send(self, message=msg)
            contribution = self.assertExists(
                    models.Contribution, conversation__associations__group=self.group,
                    text__text='Text B')
            # only the non-signature attachement should be visible
            self.assertEqual(contribution.attachments.count(), 1)
