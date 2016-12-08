from .. import models
from django import template
from django.contrib.contenttypes import models as contenttypes
from features.associations import models as associations

register = template.Library()


@register.simple_tag
def conversation_associations(group):
    from django.db.models import Max
    qs = associations.Association.objects.filter(
            entity_type=contenttypes.ContentType.objects.get_for_model(group),
            entity_id=group.id,
            container_type=contenttypes.ContentType.objects.get_for_model(models.Conversation))
    qs = qs.annotate(last_activity=Max('conversation__texts__time_created'))
    return qs.order_by('-last_activity')[:4]
