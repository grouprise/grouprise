import logging

import django.db.models.signals
import django_mailbox.signals
from django.conf import settings
from django.db.models.functions import Lower
from django.dispatch import receiver

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


def get_sender(message):

    try:
        gestalt = gestalten.Gestalt.objects.annotate(email=Lower('user__email')).get(
                email=message.from_address[0].lower())
    except gestalten.Gestalt.DoesNotExist:
        try:
            gestalt = gestalten.Gestalt.objects.annotate(
                    email=Lower('user__emailaddress__email')).get(
                            email=message.from_address[0].lower())
        except gestalten.Gestalt.DoesNotExist:
            gestalt = None
    return gestalt


def is_autoresponse(msg):
    email = msg.get_email_object()

    # RFC 3834 (https://tools.ietf.org/html/rfc3834#section-5)
    if email.get('Auto-Submitted') == 'no':
        return False
    elif email.get('Auto-Submitted'):
        return True

    # non-standard fields (https://tools.ietf.org/html/rfc3834#section-3.1.8)
    if email.get('Precedence') == 'bulk':
        return True
    if email.get('X-AUTORESPONDER'):
        return True

    return False


@receiver(django_mailbox.signals.message_received)
def process_incoming_message(sender, message, **args):
    token_beg = len(settings.DEFAULT_REPLY_TO_EMAIL.split('{')[0])
    token_end = len(settings.DEFAULT_REPLY_TO_EMAIL.rsplit('}')[1])
    DOMAIN = settings.DEFAULT_REPLY_TO_EMAIL.split('@')[1]

    def create_contribution(container, gestalt, message, in_reply_to=None):
        text = message.text.strip()
        if text == '':
            text = message.html
        t = models.Text.objects.create(text=text)
        contribution = models.Contribution.objects.create(
                author=gestalt,
                container=container,
                in_reply_to=in_reply_to,
                contribution=t)
        files.File.objects.create_from_message(message, attached_to=contribution)
        return contribution

    def process_reply(address):
        token = address[token_beg:-token_end]
        try:
            in_reply_to_text = models.Contribution.objects.get_by_message_id(
                    message.get_email_object().get('In-Reply-To'))
        except models.Contribution.DoesNotExist:
            in_reply_to_text = None
        key = core.models.PermissionToken.objects.get(secret_key=token)
        sender = get_sender(message)
        if key.gestalt != sender:
            raise django.core.exceptions.PermissionDenied(
                    'Du darfst diese Benachrichtigung nicht unter dieser E-Mail-Adresse '
                    'beantworten. Du hast folgende Möglichkeiten:\n'
                    '* Melde Dich auf der Website an und beantworte die Nachricht dort.\n'
                    '* Antworte unter der E-Mail-Adresse, an die die Benachrichtigung '
                    'gesendet wurde.\n'
                    '* Füge die E-Mail-Adresse, unter der Du antworten möchtest, Deinem '
                    'Benutzerkonto hinzu.')
        if type(key.target) == Content:
            container = key.target
        else:
            container = key.target.container
        contribution = create_contribution(
                container, key.gestalt, message, in_reply_to=in_reply_to_text)
        post_create.send(sender=None, instance=contribution)

    def process_initial(address):
        local, domain = address.split('@')
        if domain != DOMAIN:
            raise ValueError('Domain does not match.')
        gestalt = get_sender(message)
        group = groups.Group.objects.get(slug=local)
        if gestalt and gestalt.user.has_perm(
                'conversations.create_group_conversation_by_email', group):
            conversation = conversations.Conversation.objects.create(subject=message.subject)
            contribution = create_contribution(conversation, gestalt, message)
            associations.Association.objects.create(
                    entity_type=group.content_type, entity_id=group.id,
                    container_type=conversation.content_type, container_id=conversation.id)
            post_create.send(sender=None, instance=contribution)
        else:
            raise django.core.exceptions.PermissionDenied(
                    'Du darfst mit dieser Gruppe kein Gespräch per E-Mail beginnen. Bitte '
                    'verwende die Schaltfläche auf der Webseite.')

    def process_message(address):
        try:
            process_reply(address)
        except core.models.PermissionToken.DoesNotExist:
            if address == settings.STADTGESTALTEN_BOT_EMAIL:
                for to_address in message.to_addresses:
                    process_initial(to_address)
            else:
                process_initial(address)

    # FIXME: use X-Stadtgestalten-to header (mailbox without domain)
    delivered_to = message.get_email_object()['Delivered-To']
    if not delivered_to:
        logger.error('Could not process message {}: no Delivered-To header'.format(message.id))
        return
    for address in [delivered_to]:
        address = address.lstrip('<')
        address = address.rstrip('>')
        if not is_autoresponse(message):
            try:
                process_message(address)
            except ValueError as e:
                logger.error('Could not process receiver {} in message {}. {}'.format(
                    address, message.id, e))
            except (groups.Group.DoesNotExist, django.core.exceptions.PermissionDenied) as e:
                logger.warning('Could not process receiver {} in message {}. {}'.format(
                    address, message.id, e))
                django.core.mail.send_mail(
                        'Re: {}'.format(message.subject).replace('\n', ' ').replace('\r', ''),
                        'Konnte die Nachricht nicht verarbeiten. {}'.format(e),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[message.from_header],
                        fail_silently=True)
        else:
            logger.warning('Ignored message {} as autoresponse'.format(message.id))
