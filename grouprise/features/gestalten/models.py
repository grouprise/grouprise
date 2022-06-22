import datetime

import django.contrib.contenttypes.models
from allauth.account import adapter as allauth_adapter
from django import urls
from django.conf import settings
from django.contrib import auth
from django.db import models
from django.utils.timezone import now
from imagekit.models import ImageSpecField
from imagekit.processors import SmartResize, Transpose

import grouprise.core
from grouprise.core.settings import CORE_SETTINGS
from grouprise.core.utils import get_random_color
from grouprise.features.contributions.models import Contribution


class GestaltQuerySet(models.QuerySet):
    def get_by_email(self, email):
        try:
            return self.get(user__email__iexact=email)
        except self.model.DoesNotExist:
            return self.get(user__emailaddress__email__iexact=email)

    def get_or_create_by_email(self, email):
        try:
            created = False
            user = self.get_by_email(email).user
        except self.model.DoesNotExist:
            user, created = auth.get_user_model().objects.get_or_create(email=email)
        if created:
            allauth_adapter.get_adapter().populate_username(None, user)
            user.set_unusable_password()
            user.save()
        return user.gestalt

    def filter_unused(self, limit: int = None, acount_creation_age_days: int = 30):
        """generator for gestalt objects which seem to be unused (or a bot)"""
        # The first login happens automatically right after registration.  We use this short time
        # frame for determining whether a user logged in only once at all (during registration).
        login_after_registration_time = datetime.timedelta(seconds=60)
        if acount_creation_age_days is None:
            recent_account_creation_time = None
        else:
            recent_account_creation_time = now() - datetime.timedelta(
                days=acount_creation_age_days
            )
        gestalt_exemptions = {
            CORE_SETTINGS.FEED_IMPORTER_GESTALT_ID,
            CORE_SETTINGS.UNKNOWN_GESTALT_ID,
        }
        count = 0
        queryset = self.model.objects.filter(
            associations=None,
            contributions=None,
            groups=None,
            images=None,
            memberships=None,
            subscriptions=None,
            versions=None,
            votes=None,
        )
        if recent_account_creation_time is not None:
            # the account was registered recently - maybe there will be the first login soon
            queryset = queryset.filter(
                user__date_joined__lt=recent_account_creation_time
            )
        for gestalt in queryset.order_by("activity_bookmark_time").prefetch_related(
            "user"
        ):
            # test a few exceptions - all remaining accounts should be disposable
            if gestalt.pk in gestalt_exemptions:
                # some users are relevant for grouprise itself
                continue
            # did the user log in again, later (after the registration)?
            # Beware, that some users may have logged in only once, as their cookie was renewed
            # periodically.  But anyway: multiple logins are a strong indicator for a non-bot.
            if gestalt.user.last_login and (
                (gestalt.user.last_login - gestalt.user.date_joined)
                > login_after_registration_time
            ):
                # the user logged in at least twice - it seems to be human
                continue
            # this seems to be really a bot (or an unused account)
            yield gestalt
            count += 1
            if (limit is not None) and (count >= limit):
                break


class Gestalt(grouprise.core.models.Model):
    is_group = False

    about = models.TextField("Selbstauskunft", blank=True)
    avatar = grouprise.core.models.ImageField(blank=True)
    avatar_64 = ImageSpecField(
        source="avatar", processors=[Transpose(), SmartResize(64, 64)], format="PNG"
    )
    avatar_color = models.CharField(max_length=7, default=get_random_color)
    background = grouprise.core.models.ImageField("Hintergrundbild", blank=True)
    background_cover = ImageSpecField(
        source="background",
        processors=[Transpose(), SmartResize(1140, 456)],
        format="JPEG",
    )
    public = models.BooleanField(
        "Benutzerseite veröffentlichen",
        default=False,
        help_text="Öffentliche Benutzerseiten sind für alle Besucherinnen sichtbar.",
    )
    score = models.IntegerField(default=0)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    receives_builtin_inbox_notifications = models.BooleanField(
        "Empfange Benachrichtigungen auf der Plattform",
        default=True,
        help_text="Die Benachrichtigungen werden im Benutzer:innenmenü unter "
        '"Aktivität" angezeigt.',
    )
    receives_email_notifications = models.BooleanField(
        "Empfange Benachrichtigungen per E-Mail",
        default=True,
        help_text="Die Benachrichtigungen werden per E-Mail an die festgelegte "
        "Hauptadresse versendet.",
    )
    receives_matrix_notifications = models.BooleanField(
        "Empfange Benachrichtigungen per Matrix-Chat",
        default=True,
        help_text="Die Benachrichtigungen werden in verschiedene Matrix-Räume "
        "zugestellt. Sie können auch mit einer App auf mobilen Geräten gelesen werden.",
    )

    associations = django.contrib.contenttypes.fields.GenericRelation(
        "associations.Association",
        content_type_field="entity_type",
        object_id_field="entity_id",
        related_query_name="gestalt",
    )

    objects = models.Manager.from_queryset(GestaltQuerySet)()

    @property
    def name(self):
        return " ".join(filter(None, [self.user.first_name, self.user.last_name]))

    @property
    def slug(self):
        return self.user.username

    def __str__(self):
        return self.name or self.slug

    def can_login(self):
        """some accounts are created with unusable passwords (see `get_or_create_by_email`)"""
        return self.user.has_usable_password()

    def delete(self, *args, **kwargs):
        data = self.get_data()
        unknown_gestalt = Gestalt.objects.get(id=CORE_SETTINGS.UNKNOWN_GESTALT_ID)
        data["associations"].update(entity_id=unknown_gestalt.id)
        data["contributions"].update(author=unknown_gestalt)
        data["images"].update(creator=unknown_gestalt)
        data["memberships_created"].update(created_by=unknown_gestalt)
        data["versions"].update(author=unknown_gestalt)
        data["votes"].update(voter=unknown_gestalt)
        self.user.delete()

    def get_absolute_url(self):
        if self.public:
            return self.get_profile_url()
        else:
            return self.get_contact_url()

    def get_absolute_url_for_user(self, user):
        if user and user.has_perm("gestalten.view", self):
            return self.get_profile_url()
        else:
            return self.get_contact_url()

    def get_contact_url(self):
        return urls.reverse("create-gestalt-conversation", args=(self.pk,))

    def get_data(self):
        """
        Return all data directly related to this gestalt. May be used e.g. in conjunction with
        deleting users.
        """
        data = {}
        data["gestalt"] = self
        data["user"] = self.user

        # data['groups_created'] = ?
        data["memberships"] = self.memberships
        data["subscriptions"] = self.subscriptions
        data["tokens"] = self.permissiontoken_set
        data["settings"] = self.settings

        data["associations"] = self.associations
        data["contributions"] = Contribution.objects_with_deleted.filter(author=self)
        data["images"] = self.images
        data["memberships_created"] = self.memberships_created
        data["versions"] = self.versions
        data["votes"] = self.votes
        return data

    def get_profile_url(self):
        return urls.reverse("entity", args=[self.user.username])

    # FIXME: move to template filter
    def get_initials(self):
        import re

        initials = ""
        for w in str(self).split():
            m = re.search("[a-zA-Z0-9]", w)
            initials += m.group(0) if m else ""
        return initials


class GestaltSetting(models.Model):
    class Meta:
        unique_together = ("gestalt", "category", "name")

    gestalt = models.ForeignKey(
        "gestalten.Gestalt", on_delete=models.CASCADE, related_name="settings"
    )
    category = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=255)
    value = models.TextField()
