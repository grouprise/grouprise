import django.db.models.signals
from django.dispatch import receiver

from grouprise.features.contributions.notifications import ContributionCreated
from grouprise.features.contributions.tasks import send_contribution_notifications


post_create = django.dispatch.Signal(providing_args=['instance'])


@receiver(post_create)
def contribution_created(sender, instance, **kwargs):
    # send mails synchronously via default EMAIL_BACKEND
    ContributionCreated.send_all(instance, use_sync_email_backend=True)
    # send mails asynchronously (task queue) via ASYNC_EMAIL_BACKEND
    send_contribution_notifications(instance)
