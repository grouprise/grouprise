import math
from typing import Iterable, Optional

from django.db.models import QuerySet
from taggit.models import Tag

from .settings import TAG_SETTINGS


def get_slug(tag_name):
    try:
        return Tag.objects.get(name=tag_name).slug
    except Tag.DoesNotExist:
        return Tag().slugify(tag_name)


def get_tag_render_data(name: str):
    tag_parts = name.split(":", 1)
    if len(tag_parts) == 2:
        tag_group = tag_parts[0]
        tag_name = tag_parts[1]
    else:
        tag_group = None
        tag_name = name
    return tag_group, tag_name


def get_featured_tags(qs: Optional[QuerySet] = None) -> QuerySet:
    qs = qs or Tag.objects.all()
    return qs.filter(id__in=TAG_SETTINGS.FEATURED_TAG_IDS)


def get_sorted_featured_tags(qs: Optional[QuerySet] = None) -> Iterable[Tag]:
    def _get_sort_index(tag):
        try:
            return TAG_SETTINGS.FEATURED_TAG_IDS.index(tag.id)
        except ValueError:
            return math.inf

    tags: Iterable[Tag] = get_featured_tags(qs)
    return sorted(tags, key=_get_sort_index)
