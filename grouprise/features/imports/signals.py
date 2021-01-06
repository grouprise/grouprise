import collections
import datetime
import email.parser
import logging
import re

import django.db.models.signals
from django.conf import settings
import django.utils.timezone
import html2text

import grouprise.core.models
from grouprise.core.notifications import DEFAULT_REPLY_TO_EMAIL
from grouprise.features.associations import models as associations
from grouprise.features.content.models import Content
from grouprise.features.contributions import models
from grouprise.features.contributions.signals import post_create
from grouprise.features.conversations import models as conversations
from grouprise.features.files import models as files
from grouprise.features.gestalten.models import Gestalt
from grouprise.features.groups import models as groups

logger = logging.getLogger(__name__)


# a message containing exactly the following subject will raise a ValueError (for the unittests)
MAGIC_SUBJECT_FOR_INTERNAL_ERROR_TEST = 'ijoo9zee7Cheisoochae2Ophie4ohx9ahyai3ux1Quae0Phu'


class MailProcessingFailure(Exception):
    """ processing failures that should be reported """


def get_sender_gestalt(from_address):
    try:
        return Gestalt.objects.get_by_email(from_address)
    except Gestalt.DoesNotExist:
        return None


def is_autoresponse(email_obj):
    # RFC 3834 (https://tools.ietf.org/html/rfc3834#section-5)
    if email_obj.get('Auto-Submitted', '').lower() == 'no':
        return False
    elif email_obj.get('Auto-Submitted'):
        return True

    # non-standard fields (https://tools.ietf.org/html/rfc3834#section-3.1.8)
    if email_obj.get('Precedence', '').lower() == 'bulk':
        return True
    if email_obj.get('X-AUTORESPONDER'):
        return True

    return False


def sanitize_subject(subject):
    return subject.replace('\n', ' ').replace('\r', '')


ParsedMailAttachment = collections.namedtuple('ParsedMailAttachment',
                                              ('content_type', 'filename', 'data', 'model_obj'))


class ParsedMailMessage(collections.namedtuple(
        'ParsedMail', ('subject', 'content', 'to_addresses', 'from_address', 'email_obj', 'id',
                       'date', 'attachments'))):
    """ neutral mail message container to be used processing a ContributionMailProcessor

    The different sources (e.g. LMTP) should produce instances of this class.
    """

    MISSING_SUBJECT_DEFAULT = 'Namenlose Nachricht'
    SIGNATURE_TEXT_MARKER = '\n-- \n'

    @classmethod
    def get_processed_content(cls, content, is_html):
        # handle None gracefully
        if not content:
            content = ''
        # unify line splits
        content = content.replace('\r\n', '\n')
        if is_html:
            # convert html to markdown
            content = html2text.html2text(content)
        else:
            # text may contain an embedded signature - remove it
            signature_position = content.find(cls.SIGNATURE_TEXT_MARKER)
            if signature_position > 0:
                content = content[:signature_position]
        # strip needs to happen after operations involving linebreaks (e.g. the signature)
        # We can strip all whitespace at the end.
        content = content.rstrip()
        # At the beginning we want to keep whitespace (except for empty lines), since the text
        # could start with a markdown item list ('  * foo\n  * bar').
        content = content.lstrip('\n')
        return content

    @classmethod
    def parse_date(cls, date_text):
        """ parse the date from a string according to RFC2822

        In case of errors or an unset/empty string the current time is returned.
        Results always refer to the current default timezone.
        """
        tz = django.utils.timezone.get_current_timezone()
        now = datetime.datetime.now(tz=tz)
        if date_text:
            try:
                parsed = email.utils.parsedate_to_datetime(date_text)
            except ValueError as exc:
                logger.warning('Failed to parse incoming message date: %s', exc)
                return now
            return parsed.astimezone(tz=tz)
        else:
            return now

    @classmethod
    def from_email_object(cls, email_obj, from_address=None):
        """ convert an email.message.EmailMessage into a ParsedMailMessage """
        if from_address is None:
            from_address = email_obj.get('From')
        if email_obj.is_multipart():
            body_part = email_obj.get_body(preferencelist=('html', 'plain'))
            if body_part is None:
                body_part = email_obj
            attachments = tuple(
                ParsedMailAttachment(part.get_content_type(), part.get_filename(),
                                     part.get_payload(decode=True), None)
                for part in email_obj.iter_attachments())
        else:
            body_part = email_obj
            attachments = ()
        # parse and convert the body_part (containing the text or html message)
        data = body_part.get_payload(decode=True)
        content = data.decode().strip() if data else ''
        text_content = cls.get_processed_content(
            content, body_part.get_content_type().lower() == 'text/html')
        return cls(email_obj.get('Subject') or cls.MISSING_SUBJECT_DEFAULT, text_content,
                   email_obj.get_all('To'), from_address, email_obj,
                   email_obj.get('Message-ID'), cls.parse_date(email_obj.get('Date')), attachments)


class ContributionMailProcessor:
    """ process an incoming contribution mail

    Recipient and content checks are conducted during processing.
    """

    PROCESSING_FAILURE_TEXT = 'Konnte die Nachricht nicht verarbeiten.'

    def __init__(self, default_reply_to_address=None, response_from_address=None):
        if default_reply_to_address is None:
            default_reply_to_address = DEFAULT_REPLY_TO_EMAIL
        if response_from_address is None:
            response_from_address = settings.DEFAULT_FROM_EMAIL
        self._reply_domain = default_reply_to_address.split('@')[1]
        self.auth_token_regex = re.compile(r'^{prefix}([^@]+){suffix}$'.format(
            prefix=re.escape(default_reply_to_address.split('{')[0]),
            suffix=re.escape(default_reply_to_address.split('}', 1)[1])), re.IGNORECASE)
        self.response_from_address = response_from_address
        self._ignore_log_message_emitted = False

    def is_mail_domain(self, domain):
        return domain.lower() == self._reply_domain.lower()

    def is_valid_groupname(self, group_name):
        try:
            groups.Group.objects.get(slug__iexact=group_name)
            return True
        except groups.Group.DoesNotExist:
            return False

    def parse_authentication_token_text(self, address):
        """ parse a potential authentication token from a recipient address without checking it """
        match = self.auth_token_regex.match(address)
        return match.groups()[0] if match else None

    def _create_contribution(self, message, container, gestalt, in_reply_to=None):
        t = models.Text.objects.create(text=message.content)
        # comments for content sent in via email are always internal by default
        public = container.is_conversation
        contribution = models.Contribution.objects.create(
                author=gestalt,
                container=container,
                in_reply_to=in_reply_to,
                contribution=t,
                public=public,
                time_created=message.date,
        )
        files.File.objects.create_from_message_attachments(message.attachments,
                                                           attached_to=contribution)
        return contribution

    def _process_authenticated_reply(self, message, auth_token_text):
        try:
            auth_token = grouprise.core.models.PermissionToken.objects.get(
                    secret_key=auth_token_text)
        except grouprise.core.models.PermissionToken.DoesNotExist:
            raise MailProcessingFailure(
                    'Das Ziel für deine Nachricht ist ungültig. Ist die dazugehörige Unterhaltung '
                    'eventuell bereits zu alt? Nach ein paar Jahren verfallen die '
                    'Antwort-Adressen für alte Beiträge automatisch. Bitte verwende die '
                    'Schaltfläche auf der Webseite, um auf alte Beiträge zu antworten.')
        sender = get_sender_gestalt(message.from_address)
        if auth_token.gestalt != sender:
            logger.warning('Rejected message <%s>: authentication mismatch', message.id)
            raise MailProcessingFailure(
                    'Mit der E-Mail-Adresse <{}> ist es dir nicht erlaubt, diese Antwort '
                    'einzusenden. Du hast nun folgende Möglichkeiten:\n'
                    '* Melde Dich auf der Website an und beantworte die Nachricht dort.\n'
                    '* Antworte unter der E-Mail-Adresse, an die die Benachrichtigung '
                    'gesendet wurde.\n'
                    '* Füge zusätzliche E-Mail-Adressen, unter denen Du antworten möchtest, '
                    'Deinem Benutzerkonto hinzu.'.format(message.from_address))
        if type(auth_token.target) == Content:
            container = auth_token.target
        else:
            container = auth_token.target.container
        try:
            in_reply_to_text = models.Contribution.objects.get_by_message_id(
                    message.email_obj.get('In-Reply-To'))
        except models.Contribution.DoesNotExist:
            in_reply_to_text = None
        contribution = self._create_contribution(message, container, auth_token.gestalt,
                                                 in_reply_to=in_reply_to_text)
        post_create.send(sender=None, instance=contribution)

    def _process_initial_thread_contribution(self, message, recipient):
        error_text = None
        try:
            local, domain = recipient.split('@')
        except ValueError:
            error_text = 'Invalid target mail address: {}'.format(recipient)
        else:
            if not self.is_mail_domain(domain):
                # This message could be part of a delivery failure response, but it should never
                # happen with a properly configured mail server.
                error_text = 'Unknown target mail domain: {} instead of {}.'.format(
                    domain, self._reply_domain)
        if error_text is not None:
            logger.error('Could not process receiver "%s" in message %s. %s',
                         recipient, message.id, error_text)
            raise MailProcessingFailure(error_text)
        gestalt = get_sender_gestalt(message.from_address)
        try:
            group = groups.Group.objects.get(slug__iexact=local)
        except groups.Group.DoesNotExist:
            raise MailProcessingFailure(
                'Es gibt keine Gruppe mit dem Namen "{}". Somit war deine Email nicht zustellbar.'
                .format(local))
        if gestalt and gestalt.user.has_perm(
                'conversations.create_group_conversation_by_email', group):
            conversation = conversations.Conversation.objects.create(subject=message.subject)
            contribution = self._create_contribution(message, conversation, gestalt)
            associations.Association.objects.create(
                    entity_type=group.content_type, entity_id=group.id,
                    container_type=conversation.content_type, container_id=conversation.id)
            post_create.send(sender=None, instance=contribution)
        else:
            logger.warning('Rejected message (%s) for <%s>: sender lacks permission',
                           message.id, recipient)
            raise MailProcessingFailure(
                    'Du darfst mit dieser Gruppe kein Gespräch per E-Mail beginnen. Bitte '
                    'verwende die Schaltfläche auf der Webseite.')

    def _process_message(self, message, recipient):
        auth_token_text = self.parse_authentication_token_text(recipient)
        if auth_token_text is None:
            self._process_initial_thread_contribution(message, recipient)
        else:
            self._process_authenticated_reply(message, auth_token_text)

    def process_message_for_recipient(self, message, recipient):
        """ handle the incoming message and create a contribution, if all checks succeed

        Raises MailProcessingFailure in case of problems.
        """
        if message.subject == MAGIC_SUBJECT_FOR_INTERNAL_ERROR_TEST:
            # for unittests
            raise ValueError('Magic Test Subject discovered: {}'
                             .format(MAGIC_SUBJECT_FOR_INTERNAL_ERROR_TEST.swapcase()))
        elif is_autoresponse(message.email_obj):
            if not self._ignore_log_message_emitted:
                logger.warning('Ignored message {} as autoresponse'.format(message.id))
                self._ignore_log_message_emitted = True
            # no response is emitted
        else:
            self._process_message(message, recipient)

    def send_error_mail_response(self, message, error_message, recipient=None,
                                 fail_silently=False):
        if recipient is None:
            recipient = message.from_address
        subject = sanitize_subject('Re: {}'.format(message.subject))
        text = '\n'.join((self.PROCESSING_FAILURE_TEXT, error_message))
        django.core.mail.send_mail(subject, text, from_email=self.response_from_address,
                                   recipient_list=[recipient], fail_silently=fail_silently)
