from .. import models
from django import template

register = template.Library()


@register.inclusion_tag('groups/_sidebar_list.html')
def sidebar_groups(user):
    return {
            'groups': models.Group.objects.order_by('-score')[:8],
            'user': user,
            }
