from django import template

from features.board.models import Note

register = template.Library()


@register.simple_tag
def get_notes(num_max):
    return Note.objects.order_by('-time_created')[:num_max]
