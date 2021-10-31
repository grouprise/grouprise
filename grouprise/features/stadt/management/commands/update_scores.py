from django.core.management.base import BaseCommand

import grouprise.core.scores
import grouprise.features.gestalten.models
import grouprise.features.groups.models


class Command(BaseCommand):
    def handle(self, *args, **options):
        """manually update the scoring of users and groups

        The score is used for sorting users and groups based on their activity.
        It should not be necessary to call this management command manually, since a periodic task
        is configured via hey (see grouprise.features.stadt.tasks).
        """
        grouprise.core.scores.update(grouprise.features.gestalten.models.Gestalt)
        grouprise.core.scores.update(grouprise.features.groups.models.Group)
