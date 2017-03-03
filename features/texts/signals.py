from . import models
from django_mailbox import signals
from django import dispatch
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@dispatch.receiver(signals.message_received)
def process_message(sender, message, **args):
    token_beg = len(settings.DEFAULT_REPLY_TO_EMAIL.split('{')[0])
    token_end = len(settings.DEFAULT_REPLY_TO_EMAIL.rsplit('}')[1])
    token = message.to_addresses[0][token_beg:-token_end]
    try:
        try:
            in_reply_to_text = models.Text.objects.get_by_message_id(
                    message.get_email_object().get('In-Reply-To'))
        except models.Text.DoesNotExist:
            in_reply_to_text = None
        key = models.ReplyKey.objects.get(key=token)
        models.Text.objects.create(
                author=key.gestalt,
                container=key.text.container,
                in_reply_to=in_reply_to_text,
                text=message.text)
    except models.ReplyKey.DoesNotExist:
        logger.error('Could not process message {}'.format(message.id))
