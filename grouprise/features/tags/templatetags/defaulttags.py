from django import template

from grouprise.features.tags.utils import get_tag_render_data

register = template.Library()


@register.inclusion_tag("tags/_tag.html", name="tag", takes_context=True)
def render_tag(context, tag, **kwargs):
    tag_group, tag_name = get_tag_render_data(tag.name)
    context.update(
        {
            "tag": {
                "group": tag_group,
                "name": tag_name,
                "slug": tag.slug,
            }
        }
    )
    context.update(kwargs)
    return context


@register.inclusion_tag("tags/_tags.html", name="tags", takes_context=True)
def render_tags(context, tags):
    context.update({"tags": tags})
    return context
