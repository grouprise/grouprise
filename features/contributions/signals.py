import logging

import django.conf
import django.db.models.signals
import django_mailbox.signals
from django.dispatch import receiver

import core.models
from features.associations import models as associations
from features.conversations import models as conversations
from features.files import models as files
from features.gestalten import models as gestalten
from features.groups import models as groups
from . import models, notifications

logger = logging.getLogger(__name__)

contribution_created = django.dispatch.Signal(providing_args=['instance'])


@receiver(contribution_created)
def send_contribution_notification(sender, instance, **kwargs):
    notifications.Contributed(instance=instance).send()


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
    token_beg = len(django.conf.settings.DEFAULT_REPLY_TO_EMAIL.split('{')[0])
    token_end = len(django.conf.settings.DEFAULT_REPLY_TO_EMAIL.rsplit('}')[1])
    DOMAIN = django.conf.settings.DEFAULT_REPLY_TO_EMAIL.split('@')[1]

    def create_contribution(container, gestalt, message, in_reply_to=None):
        t = models.Text.objects.create(text=message.text)
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
        contribution = create_contribution(
                key.target.container, key.gestalt, message, in_reply_to=in_reply_to_text)
        contribution_created.send(sender=None, instance=contribution)

    def process_initial(address):
        local, domain = address.split('@')
        if domain != DOMAIN:
            raise ValueError('Domain does not match.')
        group = groups.Group.objects.get(slug=local)
        try:
            gestalt = gestalten.Gestalt.objects.get(
                    user__emailaddress__email=message.from_address[0])
        except gestalten.Gestalt.DoesNotExist:
            gestalt = None
        if gestalt and gestalt.user.has_perm(
                'conversations.create_group_conversation_by_email', group):
            conversation = conversations.Conversation.objects.create(subject=message.subject)
            contribution = create_contribution(conversation, gestalt, message)
            associations.Association.objects.create(
                    entity_type=group.content_type, entity_id=group.id,
                    container_type=conversation.content_type, container_id=conversation.id)
            contribution_created.send(sender=None, instance=contribution)
        else:
            raise django.core.exceptions.PermissionDenied(
                    'Du darfst mit dieser Gruppe kein Gespräch per E-Mail beginnen. Bitte '
                    'verwende die Schaltfläche auf der Webseite.')

    for address in message.to_addresses:
        if not is_autoresponse(message):
            try:
                process_reply(address)
            except core.models.PermissionToken.DoesNotExist:
                try:
                    process_initial(address)
                except (
                        groups.Group.DoesNotExist, ValueError,
                        django.core.exceptions.PermissionDenied) as e:
                    logger.error('Could not process receiver {} in message {}'.format(
                        address, message.id))
                    django.core.mail.send_mail(
                            'Re: {}'.format(message.subject),
                            'Konnte die Nachricht nicht verarbeiten. {}'.format(e),
                            from_email=django.conf.settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[message.from_header],
                            fail_silently=True)
        else:
            logger.warning('Ignored message {} as autoresponse'.format(message.id))
