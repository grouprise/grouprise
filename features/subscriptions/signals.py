from . import notifications
from core import signals
from content import models


connections = [
    signals.connect_notification(
        signals.model_created, notifications.Commented,
        instance='comment',
        senders=[models.Comment],
        ),
]
