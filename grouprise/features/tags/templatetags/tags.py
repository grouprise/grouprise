from django import template
from taggit.models import Tag

from grouprise.features.tags.settings import TAG_SETTINGS

register = template.Library()


@register.inclusion_tag("tags/_sidebar_list.html")
def sidebar_tags():
    tags = Tag.objects.filter(id__in=TAG_SETTINGS.FEATURED_TAG_IDS).order_by("name")
    return {"tags": tags}
