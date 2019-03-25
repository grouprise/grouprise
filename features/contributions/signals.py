import django.db.models.signals
from django.dispatch import receiver

from features.contributions.notifications import ContributionCreated
from features.contributions.tasks import send_contribution_notifications


post_create = django.dispatch.Signal(providing_args=['instance'])


@receiver(post_create)
def contribution_created(sender, instance, **kwargs):
    # send mails synchronously via default EMAIL_BACKEND
    ContributionCreated.send_all(instance)
    # send mails asynchronously (task queue) via ASYNC_EMAIL_BACKEND
    send_contribution_notifications(instance)
