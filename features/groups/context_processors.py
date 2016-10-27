from . import models
from django.conf import settings
from django.contrib.auth import hashers
from features.groups import models as groups_models


def groups(request):
    return {
            'about_group': models.Group.objects.filter(id=settings.ABOUT_GROUP_ID).first(),
            'active_groups': models.Group.objects.order_by('-score')[:8],
            'num_groups': models.Group.objects.count(),
            }
