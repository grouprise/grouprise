import datetime
from typing import Union

import django
from django import urls
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import gettext as _
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit, Transpose
from taggit.managers import TaggableManager

import grouprise.core.models
from grouprise.core.settings import CORE_SETTINGS
from grouprise.core.utils import get_random_color
from grouprise.features.gestalten.models import Gestalt
from grouprise.features.stadt.models import EntitySlugField


class GroupManager(models.Manager):
    def operator_group(self):
        return self.get_queryset().filter(id=CORE_SETTINGS.OPERATOR_GROUP_ID).first()


class Group(grouprise.core.models.Model):
    is_group = True

    date_created = models.DateField(default=datetime.date.today)
    time_modified = models.DateTimeField(auto_now=True)
    gestalt_created = models.ForeignKey(
        "gestalten.Gestalt",
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
    )
    name = models.CharField("Name", max_length=255)
    score = models.IntegerField(default=0)
    slug = EntitySlugField(
        _("Path of the group's site"),
        unique=True,
        help_text=_("Will be used for referencing the group"),
    )
    address = models.TextField(_("Address"), blank=True)
    avatar = grouprise.core.models.ImageField(
        blank=True,
        help_text=_(
            "An avatar is a small square image, " "used to identify the group."
        ),
    )
    avatar_64 = ImageSpecField(
        source="avatar", processors=[Transpose(), ResizeToFit(64, 64)], format="PNG"
    )
    avatar_256 = ImageSpecField(
        source="avatar", processors=[Transpose(), ResizeToFit(256, 256)], format="PNG"
    )
    avatar_color = models.CharField(max_length=7, default=get_random_color)
    date_founded = models.DateField(
        _("Group founded"),
        default=datetime.date.today,
        help_text=_("Approximate date of group creation"),
    )
    description = models.TextField(
        _("Short description"),
        blank=True,
        default="",
        max_length=200,
        help_text=_("At most 200 characters"),
    )
    logo = grouprise.core.models.ImageField(
        blank=True,
        help_text=_("The logo is visible in the right area at the group page."),
    )
    logo_sidebar = ImageSpecField(
        source="logo", processors=[Transpose(), ResizeToFit(400)], format="PNG"
    )
    url = models.URLField(_("External website"), blank=True)
    url_import_feed = models.BooleanField(
        _("Import contributions from website"),
        default=False,
        help_text=_(
            "Try to automatically import public contributions of this website "
            "on the group page"
        ),
    )

    closed = models.BooleanField(
        _("Restricted group"),
        default=False,
        help_text=_("Only members can add new members to restricted groups."),
    )

    tags = TaggableManager(verbose_name=_("Tags"), blank=True)

    associations = django.contrib.contenttypes.fields.GenericRelation(
        "associations.Association",
        content_type_field="entity_type",
        object_id_field="entity_id",
        related_query_name="group",
    )

    members = models.ManyToManyField(
        "gestalten.Gestalt",
        through="memberships.Membership",
        through_fields=("group", "member"),
        related_name="groups",
    )

    subscriptions = GenericRelation(
        "subscriptions.Subscription",
        content_type_field="subscribed_to_type",
        object_id_field="subscribed_to_id",
        related_query_name="group",
    )

    objects = GroupManager()

    def __str__(self):
        return self.name

    def delete(self):
        # first remove all objects, which are connected via generic relations
        self.associations.delete()
        self.subscriptions.delete()
        super().delete()

    def get_absolute_url(self):
        return self.get_profile_url()

    def get_profile_url(self):
        return urls.reverse("entity", args=[self.slug])

    def get_cover_url(self):
        url = None
        intro_gallery = (
            self.associations.exclude_deleted()
            .filter_galleries()
            .filter(pinned=True, public=True)
            .order_content_by_time_created()
            .first()
        )
        if intro_gallery:
            url = intro_gallery.container.gallery_images.first().image.preview_group.url
        return url

    # FIXME: move to template filter
    # TODO: when removed check api
    def get_initials(self):
        import re

        # we prefer initials for all non-trivial terms - but we collect the other initials, as well
        initials = ""
        initials_without_short_terms = ""
        for w in self.name.split():
            m = re.search("[a-zA-Z0-9]", w)
            if not m:
                continue
            initials += m.group(0)
            if w.lower() not in (
                "der",
                "die",
                "das",
                "des",
                "dem",
                "den",
                "an",
                "am",
                "um",
                "im",
                "in",
            ):
                initials_without_short_terms += m.group(0)
        # prefer the non-trivial one - otherwise pick the full one (and hope it is not empty)
        return (
            initials_without_short_terms if initials_without_short_terms else initials
        )

    @property
    def subscribers(self):
        return Gestalt.objects.filter(subscriptions__group=self)

    def get_latest_activity_time(self) -> Union[datetime.datetime, None]:
        most_recent = self.associations.order_content_by_time_created(
            ascending=False
        ).first()
        if most_recent is None:
            last_activity = None
        else:
            container = most_recent.container
            if container.is_conversation:
                last_activity = container.contributions.first().time_created
            else:
                last_activity = container.versions.first().time_created
        return last_activity
