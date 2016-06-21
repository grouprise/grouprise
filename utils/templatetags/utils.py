from django import template

register = template.Library()

@register.filter
def cuttrailing(s1, s2):
    if s1.endswith(s2):
        return s1[:-len(s2)]
    return s1

@register.filter
def limit(indexable, count):
    return indexable[:count]

@register.filter
def override(override, overridden):
    if type(override) == type(overridden):
        return override
    else:
        return overridden
