from django import http
from django.conf import settings

from . import models


def gestalt(request):
    if request.user.is_authenticated():
        return {'gestalt': request.user.gestalt}
    else:
        return {}


def get_group_by_any_field(request, **kwargs):
    group = None
    for field, arg_key in kwargs.items():
        try:
            kwarg = request.resolver_match.kwargs.get(arg_key)
            group = models.Group.objects.get(**{field: kwarg})
            break
        except models.Group.DoesNotExist:
            continue
    return kwarg, group


def groups(request):
    kwarg, group = get_group_by_any_field(request, pk='group_pk', slug='group_slug')
    if not group and kwarg:
        raise http.Http404('Group not found by argument {}.'.format(kwarg))
    return {
            'about_group': models.Group.objects.get(id=settings.ABOUT_GROUP_ID),
            'group': group,
            'group_list': models.Group.objects.all(),
            }


def statistics(request):
    return {
            'gestalt_count': models.Gestalt.objects.count, 
            'group_count': models.Group.objects.count
            }
