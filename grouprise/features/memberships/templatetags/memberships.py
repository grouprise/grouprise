from .. import models
from django import template

register = template.Library()


@register.filter
def is_member(gestalt, group):
    return models.Membership.objects.filter(group=group, member=gestalt).exists()


@register.filter
def membership(gestalt, group):
    return models.Membership.objects.filter(group=group, member=gestalt or None).first()


@register.filter
def favorite_groups(gestalt):
    return gestalt.memberships.select_related("group").order_by_gestalt_activity(
        gestalt
    )
