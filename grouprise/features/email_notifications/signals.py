from datetime import timedelta

from django.utils.timezone import now

from grouprise.core.tasks import auto_task
from grouprise.features.content.models import Content


def send_email_notifications(instance):
    """Creates a task for sending email notifications for a newly created instance.

    This signal handler is called implicitly from notifications.signals.

    @instance is either a Content or a Contribution instance.
    """
    if isinstance(instance, Content):
        if now() - instance.versions.last().time_created < timedelta(weeks=1):
            auto_task(instance)
    else:
        auto_task(instance)
