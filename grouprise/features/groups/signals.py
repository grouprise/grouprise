from django.db.models.signals import post_save
from django.dispatch import receiver

import grouprise.core
from grouprise.core.utils import slugify
from grouprise.features.gestalten import models as gestalten
from grouprise.features.stadt.forms import ENTITY_SLUG_BLACKLIST
from . import models


@receiver(post_save, sender=models.Group)
def post_group_save(sender, instance, created, **kwargs):
    if created:
        instance.slug = grouprise.core.models.get_unique_slug(
                models.Group, {'slug': slugify(instance.name)},
                reserved_slugs=ENTITY_SLUG_BLACKLIST,
                reserved_slug_qs=gestalten.Gestalt.objects,
                reserved_slug_qs_field='user__username')
        instance.save()
