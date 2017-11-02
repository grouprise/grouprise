import datetime
from email.utils import formatdate
import hashlib
import logging
import smtplib
import uuid

from django.apps import apps
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from django.template import loader

from core.models import PermissionToken
from . import models

logger = logging.getLogger(__name__)


class Notification:
    @classmethod
    def send_all(cls, instance):
        for recipient, kwargs in cls.get_recipients(instance).items():
            cls(instance).send(recipient, **kwargs)

    def __init__(self, instance):
        self.object = instance
        self.site = Site.objects.get_current()

    def create_token(self):
        token = PermissionToken(feature_key='notification-reply', gestalt=self.recipient)
        token.target = self.object
        token.save()
        return token

    def get_attachments(self):
        """
        Return a list of filenames to use as attachments.
        """
        return []

    def get_body(self):
        context = self.get_context_data()
        context.update({'site': self.site})
        template = loader.get_template(self.get_template_name())
        template.backend.engine.autoescape = False
        return template.render(context)

    def get_context_data(self, **kwargs):
        return kwargs

    def get_date(self):
        return formatdate(localtime=True)

    def get_formatted_recipient(self):
        return '{} <{}>'.format(self.recipient, self.recipient.user.email)

    def get_formatted_reply_address(self, token):
        return '<{}>'.format(settings.DEFAULT_REPLY_TO_EMAIL.format(
                reply_key=token.secret_key))

    def get_formatted_sender(self):
        sender = self.get_sender()
        name = ''
        if sender: # and recipient_attrs.get('with_name', True):
            name = '{} via '.format(sender)
        from_email = '{name}{site} <{email}>'.format(
                name=name,
                site=self.site.name,
                email=self.get_sender_email())
        return from_email

    def get_headers(self, **kwargs):
        kwargs.update(self.get_thread_headers())
        token = self.get_reply_token()
        if token:
            kwargs['Reply-To'] = self.get_formatted_reply_address(token)
        return kwargs

    def get_message(self):
        headers = self.get_headers(Date=self.get_date())
        subject_prefix = '[{}] '.format(self.group.slug) if self.group else ''
        subject = subject_prefix + self.get_subject()
        return mail.EmailMessage(
                body=self.get_body(), from_email=self.get_formatted_sender(),
                headers=headers, subject=subject,
                to=[self.get_formatted_recipient()])

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

    def get_reply_token(self):
        return None

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

    def get_thread_headers(self):
        def format_message_id(message_id, recipient):
            # The reference towards the recipient is not a security measure, thus
            # collisions (due the capping of 16 bytes) are acceptable.
            recipient_token = hashlib.sha256(recipient.user.email.encode("utf-8")).hexdigest()[:16]
            return '<{}-{}@{}>'.format(message_id, recipient_token, self.site.domain)

        headers = {}
        message_id, parent_id, reference_ids = self.get_message_ids()
        headers['Message-ID'] = format_message_id(message_id, self.recipient)
        if parent_id:
            headers['In-Reply-To'] = format_message_id(parent_id, self.recipient)
            if parent_id not in reference_ids:
                reference_ids.append(parent_id)
        if reference_ids:
            headers['References'] = ' '.join([format_message_id(ref_id, self.recipient)
                                              for ref_id in reference_ids])
        return headers

    def send(self, recipient, **kwargs):
        self.recipient = recipient
        self.kwargs = kwargs
        association = kwargs.get('association')
        if association and association.entity.is_group:
            self.group = association.entity
        else:
            self.group = None

        # construct message
        message = self.get_message()

        # add attachments
        for file_name in self.get_attachments():
            message.attach_file(file_name)

        # we don't expect errors when sending mails because we just pass mails to django-mailer
        message.send()
