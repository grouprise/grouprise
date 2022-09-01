from django.dispatch import receiver
from huey.contrib.djhuey import db_task

from grouprise.core.signals import post_create
from grouprise.features.builtin_inbox_notifications.notifications import (
    BuiltinInboxNotifications,
)
from grouprise.features.email_notifications.notifications import (
    EmailNotifications,
)
from grouprise.features.matrix_chat.notifications import MatrixNotifications
from grouprise.features.notifications.notifications import RelatedGestalten


@receiver(post_create)
def send_notifications(instance, raw=False, **_):
    if not raw:
        _send_notifications(instance)


@db_task()
def _send_notifications(instance):
    gestalten = RelatedGestalten(instance)
    BuiltinInboxNotifications(gestalten).send()
    EmailNotifications(gestalten).send()
    MatrixNotifications(gestalten).send()
