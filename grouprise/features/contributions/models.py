import django.utils.timezone
from django.contrib.contenttypes import fields as contenttypes
from django.db import models

import grouprise.core.models


class ContributionManager(models.Manager):
    def get_by_message_id(self, mid):
        import re

        if mid:
            m = re.match(r".*\.[0-9]+\.contribution\.([0-9]+)", mid)
            if m:
                return self.get(id=m.group(1))
        raise self.model.DoesNotExist

    def get_queryset(self):
        return super().get_queryset().exclude_deleted()


class PublicContributionManager(ContributionManager):
    def get_queryset(self):
        return super().get_queryset().filter_public()


class ContributionQuerySet(models.QuerySet):
    def exclude_deleted(self):
        return self.exclude(deleted__isnull=False)

    def filter_public(self):
        return self.filter(public=True)


class Contribution(grouprise.core.models.Model):
    container = contenttypes.GenericForeignKey("container_type", "container_id")
    container_id = models.PositiveIntegerField()
    container_type = models.ForeignKey(
        "contenttypes.ContentType", related_name="+", on_delete=models.CASCADE
    )

    contribution = contenttypes.GenericForeignKey(
        "contribution_type", "contribution_id"
    )
    contribution_id = models.PositiveIntegerField()
    contribution_type = models.ForeignKey(
        "contenttypes.ContentType", related_name="+", on_delete=models.CASCADE
    )

    author = models.ForeignKey(
        "gestalten.Gestalt", related_name="contributions", on_delete=models.PROTECT
    )
    attached_to = models.ForeignKey(
        "Contribution",
        null=True,
        related_name="attachments",
        on_delete=models.SET_NULL,
        blank=True,
    )
    deleted = models.DateTimeField(null=True, blank=True)
    in_reply_to = models.ForeignKey(
        "Contribution",
        null=True,
        blank=True,
        related_name="replies",
        on_delete=models.SET_NULL,
    )
    time_created = models.DateTimeField(default=django.utils.timezone.now)
    # If set to `False`, the contribution is hidden to the public in any case.
    # If `True`, the container/ association determines the visibility of the contribution.
    # See is_public_in_context_of() below.
    public = models.BooleanField(default=True)

    objects = PublicContributionManager.from_queryset(ContributionQuerySet)()
    objects_with_internal = ContributionManager.from_queryset(ContributionQuerySet)()
    objects_with_deleted = models.Manager.from_queryset(ContributionQuerySet)()

    class Meta:
        ordering = ("time_created",)

    def get_unique_id(self):
        return "{}.{}.contribution.{}".format(
            self.container_type.name, self.container.id, self.id
        )

    def is_public_in_context_of(self, entity):
        """Returns True if the contribution is public in the context of an associated entity.
        A contribution is publicly visible if it is associated publicly to an entity and is
        itself public. Returns False for unassociated entities.
        """
        if self.public:
            try:
                if entity.is_group:
                    association = self.container.associations.get(group=entity)
                else:
                    association = self.container.associations.get(gestalt=entity)
                return association.public
            except models.Model.DoesNotExist:
                return False
        else:
            return False


class Text(models.Model):
    text = models.TextField()

    contribution = contenttypes.GenericRelation(
        "contributions.Contribution",
        content_type_field="contribution_type",
        object_id_field="contribution_id",
        related_query_name="text",
    )
