from django import template

register = template.Library()

@register.filter
def limit(indexable, count):
    return indexable[:count]
