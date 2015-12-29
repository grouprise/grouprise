from django import http

from . import models


def group(request):
    try:
        slug = request.resolver_match.kwargs.get('group_slug')
        group = models.Group.objects.get(slug=slug)
    except models.Group.DoesNotExist:
        if not slug:
            group = None
        else:
            raise http.Http404('Group with slug %(slug)s not found.' % {'slug': slug})
    return {'group': group}


def stats(request):
    return {'gestalt_count': models.Gestalt.objects.count, 'group_count': models.Group.objects.count}
