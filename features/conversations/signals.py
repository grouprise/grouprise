from . import models, notifications
from core import signals
from django.contrib.contenttypes import models as contenttypes
from features.texts import models as texts


def is_conversation(text):
    return text.container_type == contenttypes.ContentType.objects.get_for_model(
            models.Conversation)


connections = [
    signals.connect_notification(
        signals.model_created,
        notifications.MessageCreated,
        instance='text',
        predicate=is_conversation,
        senders=[texts.Text],
        ),
]
