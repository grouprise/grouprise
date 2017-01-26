from core import colors, models
from django.contrib.contenttypes import fields as contenttypes
from django.core import urlresolvers
from django.db import models as django


class Group(models.Model):
    is_group = True

    date_created = django.DateField(
            auto_now_add=True)
    gestalt_created = django.ForeignKey(
            'gestalten.Gestalt',
            null=True,
            blank=True)
    name = django.CharField(
            'Name',
            max_length=255)
    score = django.IntegerField(default=0)
    slug = models.AutoSlugField(
            'Adresse der Gruppenseite',
            populate_from='name',
            reserve=['gestalt', 'stadt'],
            unique=True)

    address = django.TextField(
            'Anschrift',
            blank=True)
    avatar = django.ImageField(
            blank=True)
    avatar_color = django.CharField(
            max_length=7,
            default=colors.get_random_color)
    date_founded = django.DateField(
            'Gruppe gegründet',
            null=True,
            blank=True)
    description = django.TextField(
            'Kurzbeschreibung',
            blank=True,
            default='',
            max_length=200)
    logo = django.ImageField(
            blank=True)
    url = django.URLField(
            'Adresse im Web',
            blank=True)

    closed = django.BooleanField(
            'Geschlossene Gruppe',
            default=False,
            help_text='Nur Mitglieder können neue Mitglieder aufnehmen.')

    tags = contenttypes.GenericRelation(
            'tags.Tag',
            content_type_field='tagged_type',
            object_id_field='tagged_id',
            related_query_name='group')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return urlresolvers.reverse(
                'group', args=[type(self).objects.get(pk=self.pk).slug])

    # FIXME: move to template filter
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

    # FIXME: to be removed
    content = django.ManyToManyField(
            'content.Content',
            related_name='groups',
            through='entities.GroupContent')

    # FIXME: to be removed
    def get_head_gallery(self):
        return self.content.exclude(gallery=None).filter(
                public=True, groupcontent__pinned=True).first()
