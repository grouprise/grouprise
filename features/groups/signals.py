from . import models
from core import signals
from datetime import date


def set_group_meta(group):
    if not group.date_founded:
        group.date_founded = date.today()
    group.save()


connections = [
    signals.connect_action(
        signals.model_created,
        set_group_meta,
        senders=[models.Group],
        ),
    ]
