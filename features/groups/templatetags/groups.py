from .. import models
from django import template

register = template.Library()


@register.inclusion_tag('groups/_sidebar_list.html')
def sidebar_groups(user, exclude_group=None):
    groups = models.Group.objects.order_by('-score')
    if exclude_group:
        groups = groups.exclude(id=exclude_group.id)
    return {
            'groups': groups[:8],
            'user': user,
            }
