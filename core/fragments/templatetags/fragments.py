from core import fragments
from django import template
from django.utils import safestring

register = template.Library()


@register.simple_tag(takes_context=True)
def include_fragments(context, fragment_group):
    result = ''
    group = fragments.groups.get(fragment_group, [])
    for key in group:
        t = context.template.engine.get_template(fragments.fragments[key])
        result += t.render(context)
    return safestring.mark_safe(result)
