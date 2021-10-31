from django import template

from grouprise.features.associations.models import Association

register = template.Library()


@register.filter
def unread(association, gestalt):
    # FIXME: this complex query is evaluated once for each entry in the list
    # it is probably more performant to compute the last activity for the given association
    # and compare it to gestalt.activity_bookmark_time
    return (
        Association.objects.active_ordered_user_associations(gestalt.user)
        .filter(pk=association.pk)
        .exists()
    )
