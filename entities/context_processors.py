from . import models
from django.conf import settings

def gestalt(request):
    if request.user.is_authenticated():
        return {'gestalt': request.user.gestalt}
    else:
        return {}

def groups(request):
    return {
            'about_group': models.Group.objects.get(id=settings.ABOUT_GROUP_ID),
            'group_list': models.Group.objects.all(),
            }

def statistics(request):
    return {
            'gestalt_count': models.Gestalt.objects.count, 
            'group_count': models.Group.objects.count
            }
