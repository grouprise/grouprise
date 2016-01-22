from django import http
from django.conf import settings

from . import models


def gestalt(request):
    if request.user.is_authenticated():
        return {'gestalt': request.user.gestalt}
    else:
        return {}


def groups(request):
    try:
        slug = request.resolver_match.kwargs.get('group_slug')
        group = models.Group.objects.get(slug=slug)
    except models.Group.DoesNotExist:
        if not slug:
            group = None
        else:
            raise http.Http404('Group with slug %(slug)s not found.' % {'slug': slug})
    return {
        'about_group': models.Group.objects.get(id=settings.ABOUT_GROUP_ID),
        'group': group,
    }


def statistics(request):
    return {
        'gestalt_count': models.Gestalt.objects.count, 
        'group_count': models.Group.objects.count
    }
