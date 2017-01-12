from . import models
from django.contrib.auth import hashers


def gestalten(request):
    return {
            'num_gestalten': models.Gestalt.objects.exclude(
                user__password__startswith=hashers.UNUSABLE_PASSWORD_PREFIX).count(),
            }
