from content import models as content
from core import signals
from entities import models as entities
from features.articles import notifications as articles
from features.events import notifications as events


def is_article(association):
    try:
        return association.content.article is not None
    except content.Article.DoesNotExist:
        return False


def is_event(association):
    try:
        return association.content.event is not None
    except content.Event.DoesNotExist:
        return False


def is_gallery(association):
    try:
        return association.content.gallery is not None
    except content.Gallery.DoesNotExist:
        return False


signalpatterns = [
    signals.connect(
        signals.model_created,
        articles.Associated,
        instance='association',
        predicate=is_article,
        senders=[entities.GestaltContent, entities.GroupContent],
        ),
    signals.connect(
        signals.model_created,
        events.Associated,
        instance='association',
        predicate=is_event,
        senders=[entities.GestaltContent, entities.GroupContent],
        ),
]
