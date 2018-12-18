from huey.contrib.djhuey import task

from features.contributions.notifications import ContributionCreated


@task()
def send_contribution_notifications(instance):
    ContributionCreated.send_all(instance)
