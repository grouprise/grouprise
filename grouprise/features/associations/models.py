from django.contrib.contenttypes import fields as contenttypes
from django.db import models
from django.utils.translation import gettext as _

import grouprise.core.models
from . import querysets


class Association(grouprise.core.models.Model):
    pinned = models.BooleanField(
        _("Attach to the intro of the group"),
        default=False,
        help_text=_(
            "Attached contributions are shown first on a group's site. You can use "
            "them for common introductions and descriptions."
        ),
    )
    public = models.BooleanField(
        _("Public"),
        default=False,
        help_text=_(
            "Public contributions are visible to visitors that are not a member of "
            "the group. Members and subscribers will receive notifications."
        ),
    )
    slug = models.SlugField(
        _("Short name"),
        default=None,
        null=True,
        help_text=_(
            "Among other things the short name is used as part of the web address of "
            "a contribution."
        ),
    )

    deleted = models.DateTimeField(null=True, blank=True)

    container = contenttypes.GenericForeignKey("container_type", "container_id")
    container_id = models.PositiveIntegerField()
    container_type = models.ForeignKey(
        "contenttypes.ContentType",
        related_name="container_associations",
        on_delete=models.CASCADE,
    )

    entity = contenttypes.GenericForeignKey("entity_type", "entity_id")
    entity_id = models.PositiveIntegerField()
    entity_type = models.ForeignKey(
        "contenttypes.ContentType",
        related_name="entity_associations",
        on_delete=models.CASCADE,
    )

    objects = models.Manager.from_queryset(querysets.Association)()

    class Meta:
        unique_together = ("entity_id", "entity_type", "slug")

    def __str__(self):
        return str(self.container)

    def get_absolute_url(self):
        return self.container.get_url_for(self)
