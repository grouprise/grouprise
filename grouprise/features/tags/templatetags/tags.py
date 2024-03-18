from django import template

from grouprise.features.tags.utils import get_sorted_featured_tags

register = template.Library()


@register.inclusion_tag("tags/_sidebar_list.html")
def sidebar_tags():
    return {"tags": get_sorted_featured_tags()}
