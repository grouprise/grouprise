from . import notifications
from core import signals
from content import models as content
from entities import models as entities


def is_message(association):
    try:
        return (
                association.content.article is not None
                and not association.content.public)
    except content.Article.DoesNotExist:
        return False


connections = [
    signals.connect_notification(
        signals.model_created, notifications.Associated,
        instance='association',
        predicate=is_message,
        senders=[entities.GestaltContent, entities.GroupContent],
        ),
]
