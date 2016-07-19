from .. import models
from django import template

register = template.Library()


@register.filter
def is_member(gestalt, group):
    return models.Membership.objects.filter(
            group=group, member=gestalt).exists()
