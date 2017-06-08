from django.core.management.base import BaseCommand

import core.scores
import features.gestalten.models
import features.groups.models


class Command(BaseCommand):

    def handle(self, *args, **options):
        core.scores.update(features.gestalten.models.Gestalt)
        core.scores.update(features.groups.models.Group)
