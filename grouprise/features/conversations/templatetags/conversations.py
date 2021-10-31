from django import template
from grouprise.features.associations import models as associations

register = template.Library()


@register.simple_tag
def conversation_associations(user, group):
    return (
        associations.Association.objects.ordered_user_conversations(user)
        .filter_group_containers()
        .filter(entity_id=group.id)[:4]
    )
