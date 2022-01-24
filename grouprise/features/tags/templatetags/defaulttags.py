from django import template

from grouprise.features.tags.utils import get_tag_render_data

register = template.Library()


@register.inclusion_tag("tags/_tag.html", name="tag")
def render_tag(tag):
    tag_group, tag_name = get_tag_render_data(tag.name)
    return {
        "tag": {
            "group": tag_group,
            "name": tag_name,
            "slug": tag.slug,
        }
    }


@register.inclusion_tag("tags/_tags.html", name="tags")
def render_tags(tags):
    return {"tags": tags}
