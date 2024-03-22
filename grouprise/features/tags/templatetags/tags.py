from django import template

from grouprise.features.tags.utils import get_sorted_featured_tags

register = template.Library()


@register.inclusion_tag("tags/_sidebar_list.html")
def sidebar_tags():
    return {"tags": get_sorted_featured_tags()}


@register.inclusion_tag("tags/_tags.html", name="featured_tags", takes_context=True)
def render_featured_tags(context):
    context.update({"tags": get_sorted_featured_tags()})
    return context
