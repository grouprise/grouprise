import datetime
from email.utils import formatdate
import hashlib
import logging
import uuid

from django.apps import apps
from django.conf import settings
from django.core import mail
from django.template import loader

from grouprise.core.models import PermissionToken
from grouprise.core.settings import CORE_SETTINGS, get_grouprise_site
from grouprise.core.templatetags.defaultfilters import full_url as build_absolute_uri

logger = logging.getLogger(__name__)


class Notification:
    @classmethod
    def send_all(cls, instance, force=False, **extra_kwargs):
        for recipient, kwargs in cls.get_recipients(instance).items():
            if (force or not recipient.is_email_blocker) and (
                    recipient.id != CORE_SETTINGS.FEED_IMPORTER_GESTALT_ID):
                kwargs.update(extra_kwargs)
                cls(instance).send(recipient, **kwargs)

    def __init__(self, instance):
        self.object = instance
        self.site = get_grouprise_site()

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
        template = loader.get_template(self.get_template_name())
        template.backend.engine.autoescape = False
        return template.render(context)

    def get_context_data(self, **kwargs):
        kwargs['object'] = self.object
        kwargs['recipient'] = self.recipient
        kwargs['site'] = self.site
        kwargs['url'] = self.url
        kwargs.update(self.kwargs)
        return kwargs

    def get_date(self):
        return formatdate(localtime=True)

    def get_formatted_recipient(self):
        return '{} <{}>'.format(self.recipient, self.recipient.user.email)

    def get_formatted_reply_address(self, token):
        return '<{}>'.format(CORE_SETTINGS.DEFAULT_REPLY_TO_EMAIL.format(
                reply_key=token.secret_key))

    def get_formatted_sender(self):
        sender = self.get_sender()
        name = '{} via '.format(sender) if sender else ''
        if sender:
            email = CORE_SETTINGS.DEFAULT_DISTINCT_FROM_EMAIL.format(slug=sender.slug)
        else:
            email = settings.DEFAULT_FROM_EMAIL
        from_email = '{name}{site} <{email}>'.format(
                name=name,
                site=self.site.name,
                email=email)
        return from_email

    def get_headers(self, **kwargs):
        # thread headers
        kwargs.update(self.get_thread_headers())

        # reply-to with token
        token = self.get_reply_token()
        if token:
            kwargs['Reply-To'] = self.get_formatted_reply_address(token)

        # archived-at with url
        self.url = self.get_url()
        if self.url:
            kwargs['Archived-At'] = '<{}>'.format(build_absolute_uri(self.url))

        # list-id
        list_id = self.get_list_id()
        if list_id:
            kwargs['List-Id'] = list_id

        return kwargs

    def get_list_id(self):
        return None

    def get_message(self):
        headers = self.get_headers(Date=self.get_date())
        subject_prefix = 'Re: ' if self.is_reply() else ''
        subject_context = self.get_subject_context()
        if subject_context:
            subject_prefix += '[{}] '.format(subject_context)
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

    def get_subject(self):
        return self.subject

    def get_subject_context(self):
        return None

    def get_template_name(self):
        app_label = apps.get_containing_app_config(type(self).__module__).label
        return '{}/{}.txt'.format(
                app_label, type(self).__name__.lower())

    def get_thread_headers(self):
        def format_message_id(message_id, recipient):
            try:
                # The reference towards the recipient is not a security measure, thus
                # collisions (due the capping of 16 bytes) are acceptable.
                recipient_token = hashlib.sha256(recipient.user.email.encode("utf-8")) \
                        .hexdigest()[:16]
                return '<{}-{}@{}>'.format(message_id, recipient_token, self.site.domain)
            except AttributeError:
                return '<{}@{}>'.format(message_id, self.site.domain)

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

    def get_url(self):
        return None

    def is_reply(self):
        return False

    def send(self, recipient, **kwargs):
        self.recipient = recipient
        self.kwargs = kwargs

        # construct message
        message = self.get_message()

        # add attachments
        for file_name in self.get_attachments():
            message.attach_file(file_name)

        # we don't expect errors when sending mails because we just pass mails to django-mailer
        message.send()
