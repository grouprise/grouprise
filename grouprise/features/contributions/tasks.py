from huey.contrib.djhuey import db_task

from grouprise.features.contributions.notifications import ContributionCreated


@db_task()
def send_contribution_notifications(instance):
    ContributionCreated.send_all(instance, use_async_email_backend=True)
