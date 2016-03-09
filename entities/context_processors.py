from . import models
from django.conf import settings
from util import views as util_views


def gestalt(request):
    if request.user.is_authenticated():
        return {'gestalt': request.user.gestalt}
    else:
        return {}


def groups(request):
    return {
            'about_group': models.Group.objects.get(id=settings.ABOUT_GROUP_ID),
            'group': util_views.get_group_by_kwarg(request, pk='group_pk', slug='group_slug'),
            'group_list': models.Group.objects.all(),
            }


def statistics(request):
    return {
            'gestalt_count': models.Gestalt.objects.count, 
            'group_count': models.Group.objects.count
            }
