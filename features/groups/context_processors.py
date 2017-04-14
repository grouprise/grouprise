from . import models
from django.conf import settings


def groups(request):
    return {
            'about_group': models.Group.objects.filter(id=settings.ABOUT_GROUP_ID).first(),
            }
