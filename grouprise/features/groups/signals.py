import json
import logging
import subprocess

from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from huey.contrib.djhuey import task

from grouprise.core.utils import slugify
from grouprise.features.gestalten import models as gestalten
from grouprise.features.stadt.forms import ENTITY_SLUG_BLACKLIST
from .models import Group
from ...core.models import get_unique_slug

logger = logging.getLogger(__name__)


@task()
def call_hook_script(event_type: str, group: Group):
    hook_event_info_json = json.dumps(
        {
            "eventType": event_type,
            "objectType": "Group",
            "objectData": {"id": group.id, "slug": group.slug},
        }
    )
    hook_script_names = settings.GROUPRISE.get("HOOK_SCRIPT_PATHS", [])
    for script_name in hook_script_names:
        try:
            subprocess.run([script_name, hook_event_info_json])
        except FileNotFoundError:
            logger.error("Could not call hook script.")


@receiver(post_save, sender=Group)
def post_group_save(sender, instance, created, **kwargs):
    if created:
        call_hook_script("created", instance)
    else:
        call_hook_script("changed", instance)

    if created:
        instance.slug = get_unique_slug(
            Group,
            {"slug": slugify(instance.name)},
            reserved_slugs=ENTITY_SLUG_BLACKLIST,
            reserved_slug_qs=gestalten.Gestalt.objects,
            reserved_slug_qs_field="user__username",
        )
        instance.save()


@receiver(post_delete, sender=Group)
def group_deleted(sender, instance, **kwargs):
    call_hook_script("deleted", instance)
