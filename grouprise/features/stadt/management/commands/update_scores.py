from django.core.management.base import BaseCommand

import grouprise.core.scores
import grouprise.features.gestalten.models
import grouprise.features.groups.models


class Command(BaseCommand):

    def handle(self, *args, **options):
        grouprise.core.scores.update(grouprise.features.gestalten.models.Gestalt)
        grouprise.core.scores.update(grouprise.features.groups.models.Group)
