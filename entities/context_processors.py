from . import models
from django.conf import settings
from django.contrib.auth import hashers
from features.groups import models as groups_models

def groups(request):
    return {
            'about_group': groups_models.Group.objects.filter(id=settings.ABOUT_GROUP_ID).first(),
            'all_sidebar_groups': groups_models.Group.objects.scored().order_by('-score'),
            }

def statistics(request):
    return {
            'gestalt_count': models.Gestalt.objects.exclude(user__password__startswith=hashers.UNUSABLE_PASSWORD_PREFIX).count, 
            'group_count': groups_models.Group.objects.count
            }
