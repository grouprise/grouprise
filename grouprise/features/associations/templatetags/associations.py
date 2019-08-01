from django import template

from grouprise.features.associations.models import Association

register = template.Library()


@register.filter
def unread(association, gestalt):
    return Association.objects.active_ordered_user_associations(gestalt.user) \
            .filter(pk=association.pk).exists()
