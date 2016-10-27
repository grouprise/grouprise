from entities import models
from django.conf import settings
from django.contrib.auth import hashers
from features.groups import models as groups_models


def gestalten(request):
    return {
            'num_gestalten': models.Gestalt.objects.exclude(
                user__password__startswith=hashers.UNUSABLE_PASSWORD_PREFIX).count(),
            }
