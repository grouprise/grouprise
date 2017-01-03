"""
This file is part of stadtgestalten.

stadtgestalten is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

stadtgestalten is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero Public License for more details.

You should have received a copy of the GNU Affero Public License
along with stadtgestalten.  If not, see <http://www.gnu.org/licenses/>.
"""

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

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.object = kwargs.get('instance')

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

    def send(self):
        site = sites_models.Site.objects.get_current()

        def format_message_id(message_id, recipient):
            # The reference towards the recipient is not a security measure, thus
            # collisions (due the capping of 16 bytes) are acceptable.
            recipient_token = hashlib.sha256(recipient.encode("utf-8")).hexdigest()[:16]
            return '<{}-{}@{}>'.format(message_id, recipient_token, site.domain)

        for recipient, recipient_attrs in self.get_formatted_recipients():
            subject = self.get_subject()
            context = self.kwargs.copy()
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
            try:
                message.send()
            except smtplib.SMTPException:
                logger.error('Error while trying to send notification')
