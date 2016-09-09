from . import notifications
from core import signals
from content import models


connections = [
    signals.connect(
        signals.model_created, notifications.Commented,
        instance='comment',
        predicate=signals.always,
        senders=[models.Comment],
        ),
]
