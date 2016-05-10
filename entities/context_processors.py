from . import models
from django.conf import settings

def groups(request):
    return {
            'about_group': models.Group.objects.get(id=settings.ABOUT_GROUP_ID),
            'sidebar_groups': models.Group.objects.scored().order_by('-score'),
            }

def statistics(request):
    return {
            'gestalt_count': models.Gestalt.objects.count, 
            'group_count': models.Group.objects.count
            }
