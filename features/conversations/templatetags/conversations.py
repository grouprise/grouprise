from .. import models
from django import template

register = template.Library()


@register.simple_tag
def conversations(group):
    return models.Conversation.objects.filter(associations__group=group)
