import datetime
from email import utils as email_utils
import hashlib
import logging
import smtplib
import uuid

from django.apps import apps
from django.conf import settings
from django.contrib.sites import models as sites_models
from django.core import mail
from django.template import loader

from . import models

logger = logging.getLogger(__name__)


class Notification:
    generate_reply_tokens = False

    @staticmethod
    def format_recipient(gestalt):
        return '{} <{}>'.format(gestalt, gestalt.user.email)

    @classmethod
    def send_all(cls, instance):
        for recipient, attributes in cls.get_recipients(instance).items():
            cls(instance).send(recipient, attributes)

    def __init__(self, instance):
        self.object = instance

    def get_attachments(self):
        """
        Return a list of filenames to use as attachments.
        """
        return []

    def get_context_data(self, **kwargs):
        return kwargs

    def get_formatted_recipients(self):
        """
        Subclasses must define get_recipients() to return a set of recipients.
        The set may as well be a dictionary with the values being dictionaries. Each
        recipient may be assigned additional attributes:
        * `reply_key`: a string to identify replies
        * `with_name`: should senders identity be put in from header?

        If defined, the `Reply-To` header is set to DEFAULT_REPLY_TO_EMAIL with `{reply_key}`
        replaced by the reply key.
        """
        recipients = self.get_recipients()
        if self.generate_reply_tokens:
            recipients = self.get_reply_tokens(recipients)
        if type(recipients) == dict:
            return [(self.format_recipient(r), recipient_attrs)
                    for r, recipient_attrs in recipients.items()]
        else:
            return [(self.format_recipient(r), {}) for r in recipients]

    def get_reply_tokens(self, recipients):
        if type(recipients) == dict:
            result = recipients
            recipients = recipients.keys()
        else:
            result = {}
        for gestalt in recipients:
            token = models.PermissionToken.objects.create(
                    feature_key='notification-reply', gestalt=gestalt,
                    target_type=self.object.content_type, target_id=self.object.id)
            recipient_props = result.get(gestalt, {})
            recipient_props['reply_key'] = token.secret_key
            result[gestalt] = recipient_props
        return result

    def get_sender(self):
        return None

    def get_sender_email(self):
        return settings.DEFAULT_FROM_EMAIL

    def get_subject(self):
        return self.subject

    def get_template_name(self):
        app_label = apps.get_containing_app_config(type(self).__module__).label
        return '{}/{}.txt'.format(
                app_label, type(self).__name__.lower())

    def get_message_ids(self):
        """ generate a unique message ID for this specific email message and related IDs

        Most notification subclasses should implement their own specific message ID generator.
        Some notifications lack unique features, since they can be issued multiple times (e.g.
        group recommendations or membership associations).
        In these cases we pick a random ID. These subclasses do not need to overwrite this method.

        The result is a tuple of three items:
            * unique message ID
            * parent message ID (if available)
            * thread ID and other related messages (if available)
        """
        now_string = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        uuid_string = uuid.uuid4().hex[:16]
        my_id = '{}.{}'.format(now_string, uuid_string)
        return my_id, None, []

    def get_reply_key(self):
        return None

    def send(self, recipient, attributes):
        site = sites_models.Site.objects.get_current()

        def format_message_id(message_id, recipient):
            # The reference towards the recipient is not a security measure, thus
            # collisions (due the capping of 16 bytes) are acceptable.
            recipient_token = hashlib.sha256(recipient.encode("utf-8")).hexdigest()[:16]
            return '<{}-{}@{}>'.format(message_id, recipient_token, site.domain)

        recipient = self.format_recipient(recipient)
        recipient_attrs = {}
        subject = self.get_subject()
        context = self.get_context_data()
        context.update({'site': site})
        template = loader.get_template(self.get_template_name())
        template.backend.engine.autoescape = False
        body = template.render(context)
        sender = self.get_sender()
        name = ''
        if sender and recipient_attrs.get('with_name', True):
            name = '{} via '.format(sender)
        from_email = '{name}{site} <{email}>'.format(
                name=name,
                site=site.name,
                email=self.get_sender_email())
        headers = {}
        headers['Date'] = email_utils.formatdate(localtime=True)
        message_id, parent_id, reference_ids = self.get_message_ids()
        headers['Message-ID'] = format_message_id(message_id, recipient)
        if parent_id:
            headers['In-Reply-To'] = format_message_id(parent_id, recipient)
            if parent_id not in reference_ids:
                reference_ids.append(parent_id)
        if reference_ids:
            headers['References'] = ' '.join([format_message_id(ref_id, recipient)
                                              for ref_id in reference_ids])
        reply_key = recipient_attrs.get('reply_key')
        if reply_key:
            headers['Reply-To'] = '<{}>'.format(settings.DEFAULT_REPLY_TO_EMAIL.format(
                reply_key=reply_key))
        message = mail.EmailMessage(
                body=body, from_email=from_email, subject=subject,
                to=[recipient], headers=headers)
        for file_name in self.get_attachments():
            message.attach_file(file_name)
        try:
            message.send()
        except smtplib.SMTPException:
            logger.error('Error while trying to send notification')
