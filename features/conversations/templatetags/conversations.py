from django import template
from django.contrib.contenttypes import models as contenttypes
from features.associations import models as associations

register = template.Library()


@register.simple_tag
def conversation_associations(user, group):
    return associations.Association.objects.ordered_conversations(user).filter(
            entity_type=contenttypes.ContentType.objects.get_for_model(group),
            entity_id=group.id
            )[:4]
