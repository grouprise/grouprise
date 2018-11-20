import contextlib
import email.message
import os
import re
import tempfile

from aiosmtplib.errors import SMTPDataError
from django.conf import settings
from django.core import mail
from django.urls import reverse
from django_mailbox import models as mailbox_models, signals as mailbox_signals

from core import tests
from features.associations import models as associations
from features.contributions import models
from features.imports.management.commands.run_lmtpd import (
    ContributionLMTPD, POSTMASTER_ADDRESS)
from features.imports.signals import (
    ContributionMailProcessor, ParsedMailMessage, MAGIC_SUBJECT_FOR_INTERNAL_ERROR_TEST)
from features.gestalten import tests as gestalten
from features.memberships import test_mixins as memberships


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


class MailInjectLMTPMixin:

    def assertIsProcessingFailureReply(self, message):
        self.assertIn(ContributionMailProcessor.PROCESSING_FAILURE_TEXT, message.body,
                      message.body)

    def assertIsNotProcessingFailureReply(self, message):
        self.assertNotIn(ContributionMailProcessor.PROCESSING_FAILURE_TEXT, message.body,
                         message.body)

    def assemble_mail_data(self, headers, body=None):
        message = email.message.Message()
        for key, value in headers.items():
            message.add_header(key, value)
        if body:
            message.set_payload(body)
        return message.as_bytes()

    def inject_mail(
            self, from_address, recipients, data: bytes = None, filename: str = None) -> None:
        # either data or filename needs to be specified
        assert (data is None and filename is not None) or (data is not None and filename is None)
        if data is None:
            with open(filename, 'rb') as f:
                data = f.read()
        recipients = tuple(recipients)
        with ContributionLMTPD(lambda text: None) as lmtp_client:
            failed_recipients = lmtp_client.run_sync(
                lmtp_client.sendmail(from_address, recipients, data))
        return failed_recipients

    def _is_valid_recipient(self, recipient):
        with ContributionLMTPD(lambda text: None) as lmtp_client:
            return lmtp_client.run_sync(lmtp_client.verify_recipient(recipient))

    def assertValidRecipient(self, recipient):
        self.assertTrue(self._is_valid_recipient(recipient), recipient)

    def assertInvalidRecipient(self, recipient):
        self.assertFalse(self._is_valid_recipient(recipient), recipient)

    @contextlib.contextmanager
    def fresh_outbox_mails_retriever(self):
        """ this context returns a callable that retrieves all new outgoing mails

        Mails that arrived before the start of the context are ignored.
        """
        previous_outbox_count = len(mail.outbox)
        yield lambda: mail.outbox[previous_outbox_count:]


class ContentViaLMTP(MailInjectLMTPMixin, tests.Test):

    def test_reject_wrong_target_domain(self):
        # Mails with a wrong target domain should never reach us. They are probably caused by a
        # configuration error of the local mail server.
        with self.fresh_outbox_mails_retriever() as get_new_mails:
            rejections = self.inject_mail('foo@localhost', ['foo@example.org'], data=b'foo')
            self.assertEqual(1, len(rejections))
            self.assertEqual(0, len(get_new_mails()))

    def test_reject_non_existing_target_group(self):
        with self.fresh_outbox_mails_retriever() as get_new_mails:
            rejections = self.inject_mail('foo@localhost', ['foo@localhost'], data=b'foo')
            self.assertEqual(1, len(rejections))
            self.assertEqual(0, len(get_new_mails()))


class GroupMailMixin(memberships.AuthenticatedMemberMixin):

    @property
    def group_address(self):
        return '{}@localhost'.format(self.group.slug)


class GroupContentViaLMTP(GroupMailMixin, MailInjectLMTPMixin, tests.Test):

    def test_recipient_checks(self):
        self.assertInvalidRecipient('foo.org')
        self.assertInvalidRecipient('foo@example.org')
        self.assertInvalidRecipient(self.group_address.split('@')[0] + 'example.org')
        self.assertInvalidRecipient(settings.STADTGESTALTEN_BOT_EMAIL)
        self.assertValidRecipient(self.group_address)
        self.assertValidRecipient(self.group_address.swapcase())
        self.assertValidRecipient(settings.DEFAULT_REPLY_TO_EMAIL.format(reply_key='foo'))
        self.assertInvalidRecipient(
            settings.DEFAULT_REPLY_TO_EMAIL.replace('+{', '-{').format(reply_key='foo'))

    def test_internal_error_mail_handling(self):
        with self.fresh_outbox_mails_retriever() as get_new_mails:
            # The magic subject below is detected by the processing algorithm. It causes a
            # ValueError, that needs to be handled properly by the LMTP daemon.
            magic_bad_mail = self.assemble_mail_data(
                {'Subject': MAGIC_SUBJECT_FOR_INTERNAL_ERROR_TEST}, 'foo')
            self.assertRaisesRegex(
                SMTPDataError, re.escape("(451, 'Requested action aborted: error in processing')"),
                self.inject_mail, self.gestalt.user.email, [self.group_address], magic_bad_mail)
            self.assertEqual(1, len(get_new_mails()))
            self.assertIn(MAGIC_SUBJECT_FOR_INTERNAL_ERROR_TEST.swapcase(),
                          get_new_mails()[0].body)
            self.assertListEqual([POSTMASTER_ADDRESS], get_new_mails()[0].recipients(),
                                 get_new_mails()[0])

    def test_reject_initial_contribution_from_non_member(self):
        with self.fresh_outbox_mails_retriever() as get_new_mails:
            self.inject_mail('unauthorized@example.org', [self.group_address], data=b'foo')
            self.assertEqual(1, len(get_new_mails()))
            self.assertIsProcessingFailureReply(get_new_mails()[0])

    def test_discard_wrong_domain(self):
        with self.fresh_outbox_mails_retriever() as get_new_mails:
            wrong_target_domain = self.group_address.replace('@', '@x')
            rejections_count = self.inject_mail(self.gestalt.user.email, [wrong_target_domain],
                                                data=b'foo')
            self.assertEqual(1, len(rejections_count))
            self.assertEqual(0, len(get_new_mails()))

    def test_accept_initial_contribution_from_member(self):
        with self.fresh_outbox_mails_retriever() as get_new_mails:
            self.inject_mail(self.gestalt.user.email, [self.group_address], data=b'foo arrived')
            self.assertEqual(1, len(get_new_mails()))
            self.assertIsNotProcessingFailureReply(get_new_mails()[0])
            self.assertIn('foo arrived', get_new_mails()[0].body)
            # verify that the empty subject was filled with a default
            self.assertIn(ParsedMailMessage.MISSING_SUBJECT_DEFAULT, get_new_mails()[0].subject)

    def test_silently_ignored_autoresponders(self):
        for header_key, header_value, is_ignored in (('auto-submitted', 'no', False),
                                                     ('auto-submitted', 'maybe', True),
                                                     ('precedence', 'bulk', True),
                                                     ('precedence', '', False),
                                                     ('X-AUTORESPONDER', 'foo', True)):
            with self.fresh_outbox_mails_retriever() as get_new_mails:
                self.inject_mail('foo@localhost', [self.group_address],
                                 data=self.assemble_mail_data({header_key: header_value}))
                self.assertEqual(is_ignored, len(get_new_mails()) == 0,
                                 (header_key, header_value))


class ContentAttachments(GroupMailMixin, MailInjectLMTPMixin, tests.Test):

    def get_message_html_plain(self, subject, html_text, plain_text):
        message = email.message.EmailMessage()
        message.add_header('subject', subject)
        message.make_alternative()
        message.add_alternative(html_text, 'html')
        message.add_alternative(plain_text, 'text')
        return message

    def test_prefer_html_over_text(self):
        message = self.get_message_html_plain('Text Alternative1', 'hypertext1', 'plaintext1')
        self.inject_mail(self.gestalt.user.email, [self.group_address], data=message.as_bytes())
        contribution = self.assertExists(models.Contribution,
                                         conversation__subject='Text Alternative1',
                                         text__text='hypertext1')
        self.assertEqual(contribution.attachments.count(), 0)

    def test_attachment_image_is_stored(self):
        message = self.get_message_html_plain('Text Alternative2', 'hypertext2', 'plaintext2')
        content = b'image-data'
        message.add_attachment(content, maintype='image', subtype='png')
        for part in message.walk():
            if part.get_content_type() == 'image/png':
                part.replace_header('Content-Disposition', 'attachment; filename="foo.baz.png"')
        self.inject_mail(self.gestalt.user.email, [self.group_address], data=message.as_bytes())
        contribution = self.assertExists(models.Contribution,
                                         conversation__subject='Text Alternative2',
                                         text__text='hypertext2')
        self.assertEqual(contribution.attachments.count(), 1)
        file_obj = contribution.attachments.first().file.first()
        self.assertEqual(file_obj.file.size, len(content))
        # the check is only based on the content disposition (filename)
        self.assertTrue(file_obj.is_image())
        short_filename = os.path.basename(file_obj.file.path)
        self.assertTrue(short_filename.startswith('foo.baz-'), file_obj.file.path)
        self.assertTrue(short_filename.endswith('.png'), file_obj.file.path)

    def test_attachment_text_is_stored(self):
        message = self.get_message_html_plain('Text Alternative3', 'hypertext3', 'plaintext3')
        content = b'attached-text'
        message.add_attachment(content, maintype='text', subtype='plain')
        self.inject_mail(self.gestalt.user.email, [self.group_address], data=message.as_bytes())
        contribution = self.assertExists(models.Contribution,
                                         conversation__subject='Text Alternative3',
                                         text__text='hypertext3')
        self.assertEqual(contribution.attachments.count(), 1)
        file_obj = contribution.attachments.first().file.first()
        self.assertEqual(file_obj.file.size, len(content))


class ContentFormatting(GroupMailMixin, MailInjectLMTPMixin, tests.Test):

    def test_handle_plain_only(self):
        message = email.message.EmailMessage()
        message.add_header('subject', 'Plain Only')
        plain_content = '<p>HTML tags should be ignored, here.</p>'
        message.set_content(plain_content)
        self.inject_mail(self.gestalt.user.email, [self.group_address], data=message.as_bytes())
        self.assertExists(models.Contribution, conversation__subject='Plain Only',
                          text__text=plain_content)

    def test_html_conversion_simple_list(self):
        message = email.message.EmailMessage()
        message.add_header('subject', 'HTML Only')
        message.make_alternative()
        message.add_alternative('<ul><li>foo</li><li>bar</li></ul></p>', 'html')
        self.inject_mail(self.gestalt.user.email, [self.group_address], data=message.as_bytes())
        self.assertExists(models.Contribution, conversation__subject='HTML Only',
                          text__text='  * foo\n  * bar')

    def test_plain_signature_removal(self):
        message = email.message.EmailMessage()
        message.add_header('subject', 'With Signature')
        plain_content = 'foo\nbar\n-- \nbaz\n-- \nfuz'
        message.set_content(plain_content)
        self.inject_mail(self.gestalt.user.email, [self.group_address], data=message.as_bytes())
        self.assertExists(models.Contribution, conversation__subject='With Signature',
                          text__text='foo\nbar')


class ContentReplyByEmailViaLMTP(memberships.AuthenticatedMemberMixin, MailInjectLMTPMixin,
                                 tests.Test):

    def test_content_reply_by_email_lmtp(self):
        with self.fresh_outbox_mails_retriever() as get_new_mails:
            self.client.post(reverse('create-group-article', args=(self.group.slug,)),
                             {'title': 'Test', 'text': 'Test'})
            a = self.assertExists(associations.Association, content__title='Test')
            self.assertEqual(1, len(get_new_mails()))
            # generate reply message
            reply_to = get_new_mails()[0].extra_headers['Reply-To']
            self.inject_mail(self.gestalt.user.email, [reply_to],
                             data=self.assemble_mail_data({}, body="Text B"))
            self.assertExists(models.Contribution, content=a.content.get(), text__text='Text B')


class ContentReplyByEmailViaDjangoMailbox(memberships.AuthenticatedMemberMixin, tests.Test):

    def test_content_reply_by_email_mailbox(self):
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


class ConversationInitiateByEmailViaDjangoMailbox(memberships.MemberMixin, tests.Test):
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


class ConversationReplyByEmailViaLMTP(gestalten.AuthenticatedMixin, gestalten.OtherGestaltMixin,
                                      MailInjectLMTPMixin, tests.Test):

    def test_texts_reply_by_email_lmtp(self):
        with self.fresh_outbox_mails_retriever() as get_new_mails:
            self.client.post(self.get_url('create-gestalt-conversation', self.other_gestalt.pk),
                             {'subject': 'Subject A', 'text': 'Text A'})
            text_a = self.assertExists(models.Contribution, conversation__subject='Subject A')
            reply_to = get_new_mails()[0].extra_headers['Reply-To']
            self.inject_mail(self.other_gestalt.user.email, [reply_to],
                             data=self.assemble_mail_data({}, body="Text B"))
            self.assertExists(models.Contribution, conversation=text_a.conversation.get(),
                              text__text='Text B')

    def test_texts_reject_wrong_auth_token(self):
        with self.fresh_outbox_mails_retriever() as get_new_mails:
            self.client.post(self.get_url('create-gestalt-conversation', self.other_gestalt.pk),
                             {'subject': 'Subject C', 'text': 'Text C'})
            reply_to = get_new_mails()[0].extra_headers['Reply-To']
            wrong_reply_to = reply_to.swapcase()
        # start again with counting new mails for the reply
        with self.fresh_outbox_mails_retriever() as get_new_mails:
            self.inject_mail(self.other_gestalt.user.email, [wrong_reply_to],
                             data=self.assemble_mail_data({}, body="Text D"))
            self.assertEqual(1, len(get_new_mails()))
            self.assertIsProcessingFailureReply(get_new_mails()[0])
            self.assertNotExists(models.Contribution, text__text='Text D')

    def test_texts_reject_auth_token_from_wrong_sender(self):
        with self.fresh_outbox_mails_retriever() as get_new_mails:
            self.client.post(self.get_url('create-gestalt-conversation', self.other_gestalt.pk),
                             {'subject': 'Subject E', 'text': 'Text E'})
            self.assertExists(models.Contribution, conversation__subject='Subject E')
            reply_to = get_new_mails()[0].extra_headers['Reply-To']
        # start again with counting new mails for the reply
        with self.fresh_outbox_mails_retriever() as get_new_mails:
            # the token belongs to "other_gestalt" - thus "gestalt" may not use it
            self.inject_mail(self.gestalt.user.email, [reply_to],
                             data=self.assemble_mail_data({}, body="Text F"))
            self.assertEqual(1, len(get_new_mails()))
            self.assertIsProcessingFailureReply(get_new_mails()[0])
            self.assertNotExists(models.Contribution, text__text='Text F')


class ConversationReplyByEmailViaDjangoMailbox(gestalten.AuthenticatedMixin,
                                               gestalten.OtherGestaltMixin, tests.Test):

    def test_texts_reply_by_email_mailbox(self):
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


class ConversationAttachmentsViaDjangoMailbox(memberships.MemberMixin, tests.Test):

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
