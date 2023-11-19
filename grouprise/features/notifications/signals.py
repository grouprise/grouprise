import logging

from django.db import close_old_connections
from django.dispatch import receiver
from huey.contrib.djhuey import db_task

from grouprise.core.signals import post_create
from grouprise.core.tasks import TaskPriority
from .notifications import BaseNotification, RelatedGestalten


logger = logging.getLogger(__name__)
_registered_notification_backends = []


def register_notification_backend(notification_class: BaseNotification):
    """Implementations of notification backends need to register themselves"""
    if notification_class not in _registered_notification_backends:
        _registered_notification_backends.append(notification_class)


@receiver(post_create)
def send_notifications(instance, raw=False, **_):
    if not raw:
        close_old_connections()
        _send_notifications(instance)


# TODO: retry sending notifications in case of (temporary) errors, while avoiding duplicates
@db_task(priority=TaskPriority.NOTIFICATION)
def _send_notifications(instance):
    gestalten = RelatedGestalten(instance)
    for notification_class in _registered_notification_backends:
        try:
            notification_class(gestalten).send()
        except Exception as exc:
            logger.warning(
                "Failed to emit notification for %s via '%s': %s",
                gestalten,
                notification_class,
                exc,
            )
