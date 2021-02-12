from grouprise.features.email_notifications.notifications import (
    ContentCreated,
    ContributionCreated,
)


def send_content_notifications(instance):
    ContentCreated.send_all(instance)


def send_contribution_notifications(instance):
    ContributionCreated.send_all(instance)
