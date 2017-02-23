from . import models
from django_mailbox import models as mailbox, signals
from django import dispatch
from django.conf import settings

@dispatch.receiver(signals.message_received)
def process_messages(sender, message, **args):
    key = message.to_addresses[0][len(settings.DEFAULT_REPLY_TO_EMAIL.split('{')[0]):-len(settings.DEFAULT_REPLY_TO_EMAIL.rsplit('}')[1])]
    key = models.ReplyKey.objects.get(key=key)
    models.Text.objects.create(author=key.gestalt, container=key.text.container, text=message.text)
