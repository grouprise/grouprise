import logging

import django.conf
import django.db.models.signals
import django_mailbox.signals
from django.dispatch import receiver

import core.models
from features.associations import models as associations
from features.conversations import models as conversations
from features.gestalten import models as gestalten
from features.groups import models as groups
from . import models, notifications

logger = logging.getLogger(__name__)


@receiver(django.db.models.signals.post_save, sender=models.Contribution)
def send_contribution_notification(sender, instance, created, **kwargs):
    if created:
        notifications.Contributed(instance=instance).send()


@receiver(django_mailbox.signals.message_received)
def process_incoming_message(sender, message, **args):
    token_beg = len(django.conf.settings.DEFAULT_REPLY_TO_EMAIL.split('{')[0])
    token_end = len(django.conf.settings.DEFAULT_REPLY_TO_EMAIL.rsplit('}')[1])
    DOMAIN = django.conf.settings.DEFAULT_REPLY_TO_EMAIL.split('@')[1]

    def create_contribution(container, gestalt, text, in_reply_to=None):
        t = models.Text.objects.create(text=text)
        models.Contribution.objects.create(
                author=gestalt,
                container=container,
                in_reply_to=in_reply_to,
                contribution=t)

    def process_reply(address):
        token = address[token_beg:-token_end]
        try:
            in_reply_to_text = models.Contribution.objects.get_by_message_id(
                    message.get_email_object().get('In-Reply-To'))
        except models.Contribution.DoesNotExist:
            in_reply_to_text = None
        key = core.models.PermissionToken.objects.get(secret_key=token)
        create_contribution(
                key.target.container, key.gestalt, message.text, in_reply_to=in_reply_to_text)

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
            create_contribution(conversation, gestalt, message.text)
            associations.Association.objects.create(
                    entity_type=group.content_type, entity_id=group.id,
                    container_type=conversation.content_type, container_id=conversation.id)
        else:
            raise django.core.exceptions.PermissionDenied(
                    'Du darfst mit dieser Gruppe kein Gespräch per E-Mail beginnen. Bitte '
                    'verwende die Schaltfläche auf der Webseite.')

    for address in message.to_addresses:
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
