from . import notifications
from core import signals
from content import models as content
from entities import models as entities


def is_event(association):
    try:
        return association.content.event is not None
    except content.Event.DoesNotExist:
        return False


connections = [
    signals.connect_notification(
        signals.model_created, notifications.Associated,
        instance='association',
        predicate=is_event,
        senders=[entities.GestaltContent, entities.GroupContent]
        ),
]
