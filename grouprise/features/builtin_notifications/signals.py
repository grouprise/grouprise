from typing import Union

from grouprise.features.content.models import Content
from grouprise.features.contributions.models import Contribution


def send_builtin_notifications(instance: Union[Content, Contribution]):
    if isinstance(instance, Content):
        instance.versions.last().author.notifications.create()
    else:
        instance.author.notifications.create()
