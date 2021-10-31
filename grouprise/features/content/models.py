import django.contrib.contenttypes.models
import django.urls
import django.utils.timezone
from django.contrib.contenttypes import fields as contenttypes
from django.db import models
from django.db.models import Q
from taggit.managers import TaggableManager

import grouprise.core.models
from grouprise.features.gestalten import models as gestalten
from grouprise.features.groups import models as groups


class Content(grouprise.core.models.Model):
    is_conversation = False

    # FIXME: remove when django bug #28988 is fixed
    poll = models.OneToOneField(
        "polls.WorkaroundPoll",
        null=True,
        blank=True,
        related_name="content",
        on_delete=models.CASCADE,
    )

    title = models.CharField(max_length=255)
    image = models.ForeignKey(
        "images.Image", blank=True, null=True, on_delete=models.SET_NULL
    )

    place = models.CharField(blank=True, max_length=255)

    time = models.DateTimeField(blank=True, null=True)
    until_time = models.DateTimeField(blank=True, null=True)
    all_day = models.BooleanField(default=False)

    tags = TaggableManager()

    associations = contenttypes.GenericRelation(
        "associations.Association",
        content_type_field="container_type",
        object_id_field="container_id",
        related_query_name="content",
    )

    contributions = contenttypes.GenericRelation(
        "contributions.Contribution",
        content_type_field="container_type",
        object_id_field="container_id",
        related_query_name="content",
    )

    def __str__(self):
        return self.title

    def get_authors(self):
        return gestalten.Gestalt.objects.filter(
            Q(versions__content=self) | Q(contributions__content=self)
        ).distinct()

    def get_version_authors(self):
        return gestalten.Gestalt.objects.filter(versions__content=self).distinct()

    def get_associated_gestalten(self):
        return gestalten.Gestalt.objects.filter(associations__content=self)

    def get_associated_groups(self):
        return groups.Group.objects.filter(associations__content=self)

    def get_unique_id(self):
        return "content.{}".format(self.id)

    def get_url_for(self, association):
        return django.urls.reverse(
            "content", args=[association.entity.slug, association.slug]
        )

    @property
    def is_event(self):
        return self.time is not None

    @property
    def is_file(self):
        return self.versions.last().file.exists()

    @property
    def is_gallery(self):
        return self.gallery_images.count() > 0

    @property
    def is_poll(self):
        # FIXME: change when django bug #28988 has been fixed
        # return hasattr(self, 'poll')
        return self.poll is not None

    @property
    def subject(self):
        return self.title


class Version(models.Model):
    class Meta:
        ordering = ("time_created",)

    content = models.ForeignKey(
        "Content", related_name="versions", on_delete=models.CASCADE
    )

    author = models.ForeignKey(
        "gestalten.Gestalt", related_name="versions", on_delete=models.PROTECT
    )
    text = models.TextField()
    time_created = models.DateTimeField(default=django.utils.timezone.now)
