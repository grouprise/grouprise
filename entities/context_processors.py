from . import models
from django.conf import settings
from django.contrib.auth import hashers

def groups(request):
    return {
            'about_group': models.Group.objects.filter(id=settings.ABOUT_GROUP_ID).first(),
            'all_sidebar_groups': models.Group.objects.scored().order_by('-score'),
            }

def statistics(request):
    return {
            'gestalt_count': models.Gestalt.objects.exclude(user__password__startswith=hashers.UNUSABLE_PASSWORD_PREFIX).count, 
            'group_count': models.Group.objects.count
            }
