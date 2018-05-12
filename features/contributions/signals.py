import collections
import email.parser
import logging

import django.db.models.signals
import django_mailbox.signals
from django.conf import settings
from django.db.models.functions import Lower
from django.dispatch import receiver
import html2text

import core.models
from features.associations import models as associations
from features.content.models import Content
from features.conversations import models as conversations
from features.files import models as files
from features.gestalten import models as gestalten
from features.groups import models as groups
from . import models, notifications

logger = logging.getLogger(__name__)

post_create = django.dispatch.Signal(providing_args=['instance'])


@receiver(post_create)
def contribution_created(sender, instance, **kwargs):
    notifications.ContributionCreated.send_all(instance)


class MailProcessingFailure(Exception):
    """ processing failures that should be reported """


def get_sender_gestalt(from_address):

    try:
        gestalt = gestalten.Gestalt.objects.annotate(email=Lower('user__email')).get(
                email=from_address.lower())
    except gestalten.Gestalt.DoesNotExist:
        try:
            gestalt = gestalten.Gestalt.objects.annotate(
                    email=Lower('user__emailaddress__email')).get(
                            email=from_address.lower())
        except gestalten.Gestalt.DoesNotExist:
            gestalt = None
    return gestalt


def is_autoresponse(email_obj):
    # RFC 3834 (https://tools.ietf.org/html/rfc3834#section-5)
    if email_obj.get('Auto-Submitted') == 'no':
        return False
    elif email_obj.get('Auto-Submitted'):
        return True

    # non-standard fields (https://tools.ietf.org/html/rfc3834#section-3.1.8)
    if email_obj.get('Precedence') == 'bulk':
        return True
    if email_obj.get('X-AUTORESPONDER'):
        return True

    return False


@receiver(django_mailbox.signals.message_received)
def process_incoming_message(sender, message, **args):

    # FIXME: use X-Stadtgestalten-to header (mailbox without domain)
    delivered_to = message.get_email_object()['Delivered-To']
    if not delivered_to:
        logger.error('Could not process message {}: no Delivered-To header'.format(message.id))
        return
    parsed_message = ParsedMailMessage.from_django_mailbox_message(message)
    processor = ContributionMailProcessor(settings.STADTGESTALTEN_BOT_EMAIL,
                                          settings.DEFAULT_REPLY_TO_EMAIL,
                                          settings.DEFAULT_FROM_EMAIL)
    for address in [delivered_to]:
        address = address.lstrip('<')
        address = address.rstrip('>')
        try:
            processor.process_message_for_recipient(parsed_message, address)
        except MailProcessingFailure as exc:
            processor.send_error_mail_response(parsed_message, str(exc), fail_silently=True)


ParsedMailAttachment = collections.namedtuple('ParsedMailAttachment',
                                              ('content_type', 'filename', 'data', 'model_obj'))


class ParsedMailMessage(collections.namedtuple(
        'ParsedMail',
        ('subject', 'content', 'to_addresses', 'from_address', 'email_obj', 'id', 'attachments'))):
    """ neutral mail message container to be used processing a ContributionMailProcessor

    The different sources (e.g. django_mailbox or LMTP) should produce instances of this class.
    """

    @classmethod
    def from_django_mailbox_message(cls, message):
        # we ignore multiple "From:" addresses
        from_address = message.from_address[0]
        # parse the content type from the attachments
        attachments = []
        header_parser = email.parser.HeaderParser()
        for attachment in message.attachments.all():
            attachment_header = header_parser.parsestr(attachment.headers)
            parsed_attachment = ParsedMailAttachment(attachment_header.get_content_type(),
                                                     attachment_header.get_filename(), None,
                                                     attachment.document)
            attachments.append(parsed_attachment)
        if message.text:
            text_content = message.text
        else:
            text_content = html2text.html2text(message.html or "")
        return cls(message.subject, text_content, message.to_addresses, from_address,
                   message.get_email_object(), message.id, tuple(attachments))


class ContributionMailProcessor:
    """ process an incoming contribution mail

    Recipient and content checks are conducted during processing.
    """

    def __init__(self, bot_address, default_reply_to_address, response_from_address):
        self.bot_address = bot_address
        self._reply_domain = default_reply_to_address.split('@')[1]
        self._token_prefix_length = len(default_reply_to_address.split('{')[0])
        self._token_suffix_length = len(default_reply_to_address.rsplit('}')[1])
        self.response_from_address = response_from_address
        self._ignore_log_message_emitted = False

    def parse_auth_token(self, address):
        return address[self._token_prefix_length:-self._token_suffix_length]

    def _create_contribution(self, message, container, gestalt, in_reply_to=None):
        t = models.Text.objects.create(text=message.content)
        contribution = models.Contribution.objects.create(
                author=gestalt,
                container=container,
                in_reply_to=in_reply_to,
                contribution=t)
        files.File.objects.create_from_message_attachments(message.attachments,
                                                           attached_to=contribution)
        return contribution

    def parse_authentication_token(self, recipient):
        try:
            token = self.parse_auth_token(recipient)
            return core.models.PermissionToken.objects.get(secret_key=token)
        except core.models.PermissionToken.DoesNotExist:
            return None

    def _process_authenticated_reply(self, message, auth_token):
        sender = get_sender_gestalt(message.from_address)
        if auth_token.gestalt != sender:
            logger.warning('Rejected message <%s>: authentication mismatch', message.id)
            raise MailProcessingFailure(
                    'Du darfst diese Benachrichtigung nicht unter dieser E-Mail-Adresse '
                    'beantworten. Du hast folgende Möglichkeiten:\n'
                    '* Melde Dich auf der Website an und beantworte die Nachricht dort.\n'
                    '* Antworte unter der E-Mail-Adresse, an die die Benachrichtigung '
                    'gesendet wurde.\n'
                    '* Füge die E-Mail-Adresse, unter der Du antworten möchtest, Deinem '
                    'Benutzerkonto hinzu.')
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
        local, domain = recipient.split('@')
        if domain != self._reply_domain:
            error_text = 'Unknown target mail domain: {} instead of {}.'.format(domain,
                                                                                self._reply_domain)
            logger.error('Could not process receiver %s in message %s. %s',
                         recipient, message.id, error_text)
            # This message could be part of a delivery failure response, but it should never happen
            # with a properly configured mail server (this traffic would be misdirected).
            raise MailProcessingFailure(error_text)
        gestalt = get_sender_gestalt(message.from_address)
        try:
            group = groups.Group.objects.get(slug=local)
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
        auth_token = self.parse_authentication_token(recipient)
        if auth_token is None:
            if recipient == self.bot_address:
                for to_address in message.to_addresses:
                    self._process_initial_thread_contribution(message, to_address)
            else:
                self._process_initial_thread_contribution(message, recipient)
        else:
            self._process_authenticated_reply(message, auth_token)

    def process_message_for_recipient(self, message, recipient):
        """ handle the incoming message and create a contribution, if all checks succeed

        Raises MailProcessingFailure in case of problems.
        """
        if is_autoresponse(message.email_obj):
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
        subject = 'Re: {}'.format(message.subject).replace('\n', ' ').replace('\r', '')
        text = 'Konnte die Nachricht nicht verarbeiten.\n{}'.format(error_message)
        django.core.mail.send_mail(subject, text, from_email=self.response_from_address,
                                   recipient_list=[recipient], fail_silently=fail_silently)
