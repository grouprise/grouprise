from . import notifications
from core import signals
from content import models as content
from entities import models as entities


def is_gallery(association):
    try:
        return association.content.gallery is not None
    except content.Gallery.DoesNotExist:
        return False


connections = [
    signals.connect(
        signals.model_created, notifications.Associated,
        instance='association',
        predicate=is_gallery,
        senders=[entities.GestaltContent, entities.GroupContent]
        )
    ]
