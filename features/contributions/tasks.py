from huey.contrib.djhuey import db_task

from features.contributions.notifications import ContributionCreated


@db_task()
def send_contribution_notifications(instance):
    ContributionCreated.send_all(instance)
