from . import models, notifications
from core import signals
from django.contrib.contenttypes import models as contenttypes
from features.contributions import models as contributions


def is_conversation(contribution):
    return contribution.container_type == contenttypes.ContentType.objects.get_for_model(
            models.Conversation)


connections = [
    signals.connect_notification(
        signals.model_created,
        notifications.MessageCreated,
        instance='contribution',
        predicate=is_conversation,
        senders=[contributions.Contribution],
        ),
]
