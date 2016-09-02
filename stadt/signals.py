from core import signals
from entities import models as entities
from features.articles import notifications as articles


def is_article(association):
    return association.content.article is not None


def is_event(association):
    return association.content.event is not None


def is_gallery(association):
    return association.content.gallery is not None


signalpatterns = [
    signals.connect(
        signals.model_created,
        articles.Associated,
        instance='association',
        predicate=is_article,
        senders=[entities.GestaltContent, entities.GroupContent],
        )
]
