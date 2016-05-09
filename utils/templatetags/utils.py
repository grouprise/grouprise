from django import template

register = template.Library()

@register.filter
def limit(indexable, count):
    return indexable[:count]

@register.filter
def override(override, overridden):
    if type(override) == type(overridden):
        return override
    else:
        return overridden
