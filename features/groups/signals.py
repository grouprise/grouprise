import django
from django.db.models.signals import post_save
from django.dispatch import receiver

import core
from features.gestalten import models as gestalten
from . import models


@receiver(post_save, sender=models.Group)
def post_group_save(sender, instance, created, **kwargs):
    if created:
        instance.slug = core.models.get_unique_slug(
                models.Group, {'slug': core.text.slugify(instance.name)},
                reserved_slugs=django.conf.settings.ENTITY_SLUG_BLACKLIST,
                reserved_slug_qs=gestalten.Gestalt.objects,
                reserved_slug_qs_field='user__username')
        instance.save()
