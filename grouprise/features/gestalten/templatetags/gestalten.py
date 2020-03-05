from django.template import Library

register = Library()


@register.filter
def sort_gestalt_first(gestalten, first_gestalt):
    result = sorted(gestalten, key=lambda gestalt: gestalt.name.upper())
    try:
        result.remove(first_gestalt)
        result.insert(0, first_gestalt)
    except ValueError:
        pass
    return result
