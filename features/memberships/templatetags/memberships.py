from .. import models
from django import template

register = template.Library()


@register.filter
def is_member(gestalt, group):
    return models.Membership.objects.filter(
            gestalt=gestalt, group=group).exists()
