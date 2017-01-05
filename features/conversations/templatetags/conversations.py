from django import template
from features.associations import models as associations

register = template.Library()


@register.simple_tag
def conversation_associations(user, group):
    return associations.Association.objects.ordered_group_conversations(user, group)[:4]
