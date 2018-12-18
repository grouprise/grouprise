import datetime

import django
from django.contrib.contenttypes import fields as contenttypes
from django.contrib.contenttypes.fields import GenericRelation
from django import urls
from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit, Transpose

import core.models
from core import colors
from features.gestalten.models import Gestalt
from features.stadt.models import EntitySlugField


class Group(core.models.Model):
    is_group = True

    date_created = models.DateField(
            auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    gestalt_created = models.ForeignKey(
            'gestalten.Gestalt', null=True, blank=True, related_name='+',
            on_delete=models.SET_NULL)
    name = models.CharField(
            'Name',
            max_length=255)
    score = models.IntegerField(default=0)
    slug = EntitySlugField(
            'Adresse der Gruppenseite', blank=True, null=True, unique=True,
            help_text='Wird auch als Kurzname verwendet')

    address = models.TextField(
            'Anschrift',
            blank=True)
    avatar = core.models.ImageField(
            blank=True, help_text='Der Avatar ist ein kleines quadratisches Vorschaubild, '
            'an welchem sich die Gruppe leicht erkennen lässt.')
    avatar_64 = ImageSpecField(
            source='avatar', processors=[Transpose(), ResizeToFit(64, 64)], format='PNG')
    avatar_256 = ImageSpecField(
            source='avatar', processors=[Transpose(), ResizeToFit(256, 256)], format='PNG')
    avatar_color = models.CharField(
            max_length=7,
            default=colors.get_random_color)
    date_founded = models.DateField(
            'Gruppe gegründet', default=datetime.date.today,
            help_text='Ungefähres Datum der tatsächlichen Gruppengründung')
    description = models.TextField(
            'Kurzbeschreibung',
            blank=True,
            default='',
            max_length=200,
            help_text='Höchstens 200 Zeichen')
    logo = core.models.ImageField(
            blank=True, help_text='Das Logo wird auf der Gruppenseite rechts angezeigt.')
    logo_sidebar = ImageSpecField(
            source='logo', processors=[Transpose(), ResizeToFit(400)], format='PNG')
    url = models.URLField(
            'Externe Website',
            blank=True)
    url_import_feed = models.BooleanField(
            'Beiträge von Website übernehmen', default=False,
            help_text='Öffentliche Beiträge der angegebenen Website nach Möglichkeit '
            'automatisch in dieser Gruppe veröffentlichen')

    closed = models.BooleanField(
            'Geschlossene Gruppe', default=False, help_text='In eine geschlossene Gruppe '
            'können nur Mitglieder neue Mitglieder aufnehmen.')

    tags = contenttypes.GenericRelation(
            'tags.Tagged',
            content_type_field='tagged_type',
            object_id_field='tagged_id',
            related_query_name='group')

    associations = django.contrib.contenttypes.fields.GenericRelation(
            'associations.Association', content_type_field='entity_type',
            object_id_field='entity_id', related_query_name='group')

    members = models.ManyToManyField(
            'gestalten.Gestalt', through='memberships.Membership',
            through_fields=('group', 'member'), related_name='groups')

    subscriptions = GenericRelation(
            'subscriptions.Subscription', content_type_field='subscribed_to_type',
            object_id_field='subscribed_to_id', related_query_name='group')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return self.get_profile_url()

    def get_profile_url(self):
        return urls.reverse(
                'entity', args=[type(self).objects.get(pk=self.pk).slug])

    def get_cover_url(self):
        url = None
        intro_gallery = self.associations.exclude_deleted().filter_galleries() \
            .filter(pinned=True, public=True).order_content_by_time_created().first()
        if intro_gallery:
            url = intro_gallery.container.gallery_images.first().image.preview_group.url
        return url

    # FIXME: move to template filter
    # TODO: when removed check api
    def get_initials(self):
        import re
        # we prefer initials for all non-trivial terms - but we collect the other initials, as well
        initials = ''
        initials_without_short_terms = ''
        for w in self.name.split():
            m = re.search('[a-zA-Z0-9]', w)
            if not m:
                continue
            initials += m.group(0)
            if w.lower() not in ("der", "die", "das", "des", "dem",
                                 "den", "an", "am", "um", "im", "in"):
                initials_without_short_terms += m.group(0)
        # prefer the non-trivial one - otherwise pick the full one (and hope it is not empty)
        return initials_without_short_terms if initials_without_short_terms else initials

    @property
    def subscribers(self):
        return Gestalt.objects.filter(subscriptions__group=self)
