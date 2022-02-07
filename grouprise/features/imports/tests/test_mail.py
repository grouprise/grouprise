import contextlib
import email.message
import os
import re
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from aiosmtplib.errors import SMTPDataError
from django.core import mail
from django.urls import reverse

import grouprise.features.gestalten.tests
import grouprise.features.gestalten.tests.mixins
from grouprise.core import tests
from grouprise.core.settings import CORE_SETTINGS, get_grouprise_site
from grouprise.features.associations import models as associations
from grouprise.features.contributions import models
from grouprise.features.imports.mails import (
    MAGIC_SUBJECT_FOR_INTERNAL_ERROR_TEST,
    ContributionMailProcessor,
    ParsedMailMessage,
)
from grouprise.features.imports.management.commands.run_lmtpd import ContributionLMTPD
from grouprise.features.memberships import test_mixins as memberships


def get_full_address(local):
    return local + "@" + get_grouprise_site().domain


class MailInjectLMTPMixin:
    def assertIsProcessingFailureReply(self, message):
        self.assertIn(
            ContributionMailProcessor.PROCESSING_FAILURE_TEXT,
            message.body,
            message.body,
        )

    def assertIsNotProcessingFailureReply(self, message):
        self.assertNotIn(
            ContributionMailProcessor.PROCESSING_FAILURE_TEXT,
            message.body,
            message.body,
        )

    def assemble_mail_data(self, headers, body=None, attachments=None):
        """assemble an email message object based on the given arguments

        A MIME multipart mail is generated, if 'attachments' is non-empty.

        @param headers: dictionary of mail headers
        @param body: optional text body of the mail message
        @param attachments: optional list of dictionaries describing attachments.  Each dictionary
            must contain "content_type" and "payload". The key "disposition_filename" is optional.
        """
        if attachments is None:
            attachments = []
        if not attachments:
            message = email.message.Message()
        else:
            message = MIMEMultipart()
        for key, value in headers.items():
            message.add_header(key, value)
        if attachments:
            if body:
                message.attach(MIMEText(body))
            for attachment_info in attachments:
                attachment = MIMEBase(*attachment_info["content_type"].split("/", 1))
                attachment.set_payload(attachment_info["payload"])
                if "disposition_filename" in attachment_info:
                    attachment.add_header(
                        "Content-Disposition",
                        "attachment",
                        filename=attachment_info["disposition_filename"],
                    )
                message.attach(attachment)
        else:
            if body:
                message.set_payload(body)
        return message.as_bytes()

    def inject_mail(
        self, from_address, recipients, data: bytes = None, filename: str = None
    ) -> None:
        # either data or filename needs to be specified
        assert (data is None and filename is not None) or (
            data is not None and filename is None
        )
        if data is None:
            with open(filename, "rb") as f:
                data = f.read()
        recipients = tuple(recipients)
        with ContributionLMTPD(lambda text: None) as lmtp_client:
            failed_recipients = lmtp_client.run_sync(
                lmtp_client.sendmail(from_address, recipients, data)
            )
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
        """this context returns a callable that retrieves all new outgoing mails

        Mails that arrived before the start of the context are ignored.
        """
        previous_outbox_count = len(mail.outbox)
        yield lambda: mail.outbox[previous_outbox_count:]


class ContentViaLMTP(MailInjectLMTPMixin, tests.Test):
    def test_reject_wrong_target_domain(self):
        # Mails with a wrong target domain should never reach us. They are probably caused by a
        # configuration error of the local mail server.
        with self.fresh_outbox_mails_retriever() as get_new_mails:
            rejections = self.inject_mail(
                get_full_address("foo"), ["foo@example.org"], data=b"foo"
            )
            self.assertEqual(1, len(rejections))
            self.assertEqual(0, len(get_new_mails()))

    def test_reject_non_existing_target_group(self):
        with self.fresh_outbox_mails_retriever() as get_new_mails:
            rejections = self.inject_mail(
                get_full_address("foo"), [get_full_address("foo")], data=b"foo"
            )
            self.assertEqual(1, len(rejections))
            self.assertEqual(0, len(get_new_mails()))


class GroupMailMixin(memberships.MemberMixin):
    @property
    def group_address(self):
        return get_full_address(self.group.slug)


class GroupContentViaLMTP(GroupMailMixin, MailInjectLMTPMixin, tests.Test):
    def test_recipient_checks(self):
        self.assertInvalidRecipient("foo.org")
        self.assertInvalidRecipient("foo@example.org")
        self.assertInvalidRecipient(self.group_address.split("@")[0] + "example.org")
        self.assertValidRecipient(self.group_address)
        self.assertValidRecipient(self.group_address.swapcase())
        self.assertValidRecipient(
            CORE_SETTINGS.DEFAULT_REPLY_TO_EMAIL.format(reply_key="foo")
        )
        self.assertInvalidRecipient(
            CORE_SETTINGS.DEFAULT_REPLY_TO_EMAIL.replace("+{", "-{").format(
                reply_key="foo"
            )
        )

    def test_internal_error_mail_handling(self):
        with self.fresh_outbox_mails_retriever() as get_new_mails:
            # The magic subject below is detected by the processing algorithm. It causes a
            # ValueError, that needs to be handled properly by the LMTP daemon.
            magic_bad_mail = self.assemble_mail_data(
                {"Subject": MAGIC_SUBJECT_FOR_INTERNAL_ERROR_TEST}, "foo"
            )
            self.assertRaisesRegex(
                SMTPDataError,
                re.escape("(451, 'Requested action aborted: error in processing')"),
                self.inject_mail,
                self.gestalt.user.email,
                [self.group_address],
                magic_bad_mail,
            )
            self.assertEqual(1, len(get_new_mails()))
            self.assertIn(
                MAGIC_SUBJECT_FOR_INTERNAL_ERROR_TEST.swapcase(),
                get_new_mails()[0].body,
            )
            self.assertListEqual(
                [CORE_SETTINGS.POSTMASTER_EMAIL],
                get_new_mails()[0].recipients(),
                get_new_mails()[0],
            )

    def test_reject_initial_contribution_from_non_member(self):
        with self.fresh_outbox_mails_retriever() as get_new_mails:
            self.inject_mail(
                "unauthorized@example.org", [self.group_address], data=b"foo"
            )
            self.assertEqual(1, len(get_new_mails()))
            self.assertIsProcessingFailureReply(get_new_mails()[0])

    def test_discard_wrong_domain(self):
        with self.fresh_outbox_mails_retriever() as get_new_mails:
            wrong_target_domain = self.group_address.replace("@", "@x")
            rejections = self.inject_mail(
                self.gestalt.user.email, [wrong_target_domain], data=b"foo"
            )
            self.assertEqual(1, len(rejections))
            self.assertEqual(0, len(get_new_mails()))

    def test_accept_initial_contribution_from_member(self):
        with self.fresh_outbox_mails_retriever() as get_new_mails:
            self.inject_mail(
                self.gestalt.user.email, [self.group_address], data=b"foo arrived"
            )
            self.assertEqual(1, len(get_new_mails()))
            self.assertIsNotProcessingFailureReply(get_new_mails()[0])
            self.assertIn("foo arrived", get_new_mails()[0].body)
            # verify that the empty subject was filled with a default
            self.assertIn(
                ParsedMailMessage.MISSING_SUBJECT_DEFAULT, get_new_mails()[0].subject
            )

    def test_silently_ignored_autoresponders(self):
        for header_key, header_value, is_ignored in (
            ("auto-submitted", "no", False),
            ("auto-submitted", "maybe", True),
            ("precedence", "bulk", True),
            ("precedence", "", False),
            ("X-AUTORESPONDER", "foo", True),
        ):
            with self.fresh_outbox_mails_retriever() as get_new_mails:
                self.inject_mail(
                    get_full_address("foo"),
                    [self.group_address],
                    data=self.assemble_mail_data({header_key: header_value}),
                )
                self.assertEqual(
                    is_ignored, len(get_new_mails()) == 0, (header_key, header_value)
                )


class ContentAttachments(GroupMailMixin, MailInjectLMTPMixin, tests.Test):
    def get_message_html_plain(self, subject, html_text, plain_text):
        message = email.message.EmailMessage()
        message.add_header("subject", subject)
        message.make_alternative()
        message.add_alternative(html_text, "html")
        message.add_alternative(plain_text, "text")
        return message

    def test_prefer_html_over_text(self):
        message = self.get_message_html_plain(
            "Text Alternative1", "hypertext1", "plaintext1"
        )
        self.inject_mail(
            self.gestalt.user.email, [self.group_address], data=message.as_bytes()
        )
        contribution = self.assertExists(
            models.Contribution,
            conversation__subject="Text Alternative1",
            text__text="hypertext1",
        )
        self.assertEqual(contribution.attachments.count(), 0)

    def test_attachment_image_is_stored(self):
        message = self.get_message_html_plain(
            "Text Alternative2", "hypertext2", "plaintext2"
        )
        content = b"image-data"
        message.add_attachment(content, maintype="image", subtype="png")
        for part in message.walk():
            if part.get_content_type() == "image/png":
                part.replace_header(
                    "Content-Disposition", 'attachment; filename="foo.baz.png"'
                )
        self.inject_mail(
            self.gestalt.user.email, [self.group_address], data=message.as_bytes()
        )
        contribution = self.assertExists(
            models.Contribution,
            conversation__subject="Text Alternative2",
            text__text="hypertext2",
        )
        self.assertEqual(contribution.attachments.count(), 1)
        file_obj = contribution.attachments.first().file.first()
        self.assertEqual(file_obj.file.size, len(content))
        # the check is only based on the content disposition (filename)
        self.assertTrue(file_obj.is_image())
        short_filename = os.path.basename(file_obj.file.path)
        self.assertTrue(short_filename.endswith(".png"), file_obj.file.path)

    def test_attachment_text_is_stored(self):
        message = self.get_message_html_plain(
            "Text Alternative3", "hypertext3", "plaintext3"
        )
        content = b"attached-text"
        message.add_attachment(content, maintype="text", subtype="plain")
        self.inject_mail(
            self.gestalt.user.email, [self.group_address], data=message.as_bytes()
        )
        contribution = self.assertExists(
            models.Contribution,
            conversation__subject="Text Alternative3",
            text__text="hypertext3",
        )
        self.assertEqual(contribution.attachments.count(), 1)
        file_obj = contribution.attachments.first().file.first()
        self.assertEqual(file_obj.file.size, len(content))


class ContentFormatting(GroupMailMixin, MailInjectLMTPMixin, tests.Test):
    def test_handle_plain_only(self):
        message = email.message.EmailMessage()
        message.add_header("subject", "Plain Only")
        plain_content = "<p>HTML tags should be ignored, here.</p>"
        message.set_content(plain_content)
        self.inject_mail(
            self.gestalt.user.email, [self.group_address], data=message.as_bytes()
        )
        self.assertExists(
            models.Contribution,
            conversation__subject="Plain Only",
            text__text=plain_content,
        )

    def test_html_conversion_simple_list(self):
        message = email.message.EmailMessage()
        message.add_header("subject", "HTML Only")
        message.make_alternative()
        message.add_alternative("<ul><li>foo</li><li>bar</li></ul></p>", "html")
        self.inject_mail(
            self.gestalt.user.email, [self.group_address], data=message.as_bytes()
        )
        self.assertExists(
            models.Contribution,
            conversation__subject="HTML Only",
            text__text="  * foo\n  * bar",
        )

    def test_plain_signature_removal(self):
        message = email.message.EmailMessage()
        message.add_header("subject", "With Signature")
        plain_content = "foo\nbar\n-- \nbaz\n-- \nfuz"
        message.set_content(plain_content)
        self.inject_mail(
            self.gestalt.user.email, [self.group_address], data=message.as_bytes()
        )
        self.assertExists(
            models.Contribution,
            conversation__subject="With Signature",
            text__text="foo\nbar",
        )


class ContentMetaDataViaLMTP(GroupMailMixin, MailInjectLMTPMixin, tests.Test):
    def test_mail_date(self):
        """verify that the notification uses the date of the incoming mail"""
        with self.fresh_outbox_mails_retriever() as get_new_mails:
            self.inject_mail(
                self.gestalt.user.email,
                [self.group_address],
                data=b"Date: Mon, 20 Nov 1995 14:12:08 -0500\n\nfoo",
            )
            self.assertEqual(len(get_new_mails()), 1)
            self.assertEqual(
                get_new_mails()[0].extra_headers["Date"],
                "Mon, 20 Nov 1995 20:12:08 +0100",
            )


class ContentReplyByEmailViaLMTP(
    memberships.AuthenticatedMemberMixin, MailInjectLMTPMixin, tests.Test
):
    def test_content_reply_by_email_lmtp(self):
        with self.fresh_outbox_mails_retriever() as get_new_mails:
            self.client.post(
                reverse("create-group-article", args=(self.group.slug,)),
                {"title": "Test", "text": "Test"},
            )
            a = self.assertExists(associations.Association, content__title="Test")
            self.assertEqual(1, len(get_new_mails()))
            # generate reply message
            reply_to = get_new_mails()[0].extra_headers["Reply-To"]
            self.inject_mail(
                self.gestalt.user.email,
                [reply_to],
                data=self.assemble_mail_data({}, body="Text B"),
            )
            self.assertFalse(
                models.Contribution.objects.filter(
                    content=a.content.get(), text__text="Text B"
                ).exists()
            )
            self.assertTrue(
                models.Contribution.objects_with_internal.filter(
                    content=a.content.get(), text__text="Text B"
                ).exists()
            )


class ConversationInitiateByEmailViaLMTP(
    GroupMailMixin, MailInjectLMTPMixin, tests.Test
):
    def test_conversation_initiate_by_email(self):
        self.inject_mail(
            self.gestalt.user.email,
            [self.group_address],
            data=self.assemble_mail_data({}, body="Text A"),
        )
        self.assertExists(
            models.Contribution,
            conversation__associations__group=self.group,
            text__text="Text A",
        )

    def test_conversation_initiate_by_email_mixed_case_addresses(self):
        self.inject_mail(
            self.gestalt.user.email.title(),
            [self.group_address.title()],
            data=self.assemble_mail_data({}, body="Text B"),
        )
        self.assertExists(
            models.Contribution,
            conversation__associations__group=self.group,
            text__text="Text B",
        )

    def test_conversation_initiate_by_email_failing(self):
        with self.fresh_outbox_mails_retriever() as get_new_mails:
            rejections = self.inject_mail(
                self.gestalt.user.email,
                [get_full_address("not-existing")],
                data=self.assemble_mail_data({}, body="Text C"),
            )
            self.assertEqual(1, len(rejections))
            self.assertEqual(0, len(get_new_mails()))


class ConversationReplyByEmailViaLMTP(
    grouprise.features.gestalten.tests.mixins.AuthenticatedMixin,
    grouprise.features.gestalten.tests.mixins.OtherGestaltMixin,
    MailInjectLMTPMixin,
    tests.Test,
):
    def test_texts_reply_by_email_lmtp(self):
        with self.fresh_outbox_mails_retriever() as get_new_mails:
            self.client.post(
                self.get_url("create-gestalt-conversation", self.other_gestalt.pk),
                {"subject": "Subject A", "text": "Text A"},
            )
            text_a = self.assertExists(
                models.Contribution, conversation__subject="Subject A"
            )
            reply_to = get_new_mails()[0].extra_headers["Reply-To"]
            self.inject_mail(
                self.other_gestalt.user.email,
                [reply_to],
                data=self.assemble_mail_data({}, body="Text B"),
            )
            self.assertExists(
                models.Contribution,
                conversation=text_a.conversation.get(),
                text__text="Text B",
            )

    def test_texts_reject_wrong_auth_token(self):
        with self.fresh_outbox_mails_retriever() as get_new_mails:
            self.client.post(
                self.get_url("create-gestalt-conversation", self.other_gestalt.pk),
                {"subject": "Subject C", "text": "Text C"},
            )
            reply_to = get_new_mails()[0].extra_headers["Reply-To"]
            wrong_reply_to = reply_to.swapcase()
        # start again with counting new mails for the reply
        with self.fresh_outbox_mails_retriever() as get_new_mails:
            self.inject_mail(
                self.other_gestalt.user.email,
                [wrong_reply_to],
                data=self.assemble_mail_data({}, body="Text D"),
            )
            self.assertEqual(1, len(get_new_mails()))
            self.assertIsProcessingFailureReply(get_new_mails()[0])
            self.assertNotExists(models.Contribution, text__text="Text D")

    def test_texts_reject_auth_token_from_wrong_sender(self):
        with self.fresh_outbox_mails_retriever() as get_new_mails:
            self.client.post(
                self.get_url("create-gestalt-conversation", self.other_gestalt.pk),
                {"subject": "Subject E", "text": "Text E"},
            )
            self.assertExists(models.Contribution, conversation__subject="Subject E")
            reply_to = get_new_mails()[0].extra_headers["Reply-To"]
        # start again with counting new mails for the reply
        with self.fresh_outbox_mails_retriever() as get_new_mails:
            # the token belongs to "other_gestalt" - thus "gestalt" may not use it
            self.inject_mail(
                self.gestalt.user.email,
                [reply_to],
                data=self.assemble_mail_data({}, body="Text F"),
            )
            self.assertEqual(1, len(get_new_mails()))
            self.assertIsProcessingFailureReply(get_new_mails()[0])
            self.assertNotExists(models.Contribution, text__text="Text F")


class ConversationAttachmentsViaLMTP(GroupMailMixin, MailInjectLMTPMixin, tests.Test):
    def test_conversation_initiate_with_attachments(self):
        message = self.assemble_mail_data(
            {},
            body="Text B",
            attachments=[
                {"content_type": "text/plain", "payload": "foo"},
                {"content_type": "application/pgp-signature", "payload": "bar"},
            ],
        )
        self.inject_mail(self.gestalt.user.email, [self.group_address], data=message)
        contribution = self.assertExists(
            models.Contribution,
            conversation__associations__group=self.group,
            text__text="Text B",
        )
        # only the non-signature attachment should be visible
        self.assertEqual(contribution.attachments.count(), 1)
