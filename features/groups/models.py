from core import colors, models
from django.core import urlresolvers
from django.db import models as django
from entities import querysets


class Group(models.Model):
    date_created = django.DateField(
            auto_now_add=True)
    gestalt_created = django.ForeignKey(
            'entities.Gestalt',
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

    objects = django.Manager.from_queryset(querysets.Group)()

    class Meta:
        # FIXME: we should use case-insensitive ordering here
        # https://code.djangoproject.com/ticket/24747
        # https://code.djangoproject.com/ticket/26257
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return urlresolvers.reverse(
                'group', args=[type(self).objects.get(pk=self.pk).slug])

    # FIXME: move to template filter
    def get_initials(self):
        import re
        initials = ''
        for w in self.name.split():
            m = re.search('[a-zA-Z0-9]', w)
            initials += m.group(0) if m else ''
        return initials

    # FIXME: to be removed
    content = django.ManyToManyField(
            'content.Content',
            related_name='groups',
            through='entities.GroupContent')

    # FIXME: to be removed
    def get_head_gallery(self):
        return self.content.exclude(gallery=None).filter(
                public=True, groupcontent__pinned=True).first()

    # FIXME: to be removed
    def get_conversations(self, user):
        from django.db.models import Max
        from django.db.models.functions import Coalesce
        return self.content \
            .permitted(user) \
            .filter(article__isnull=False, public=False) \
            .annotate(last_comment=Max('comments__date_created')) \
            .annotate(last_activity=Coalesce("last_comment", "date_created")) \
            .order_by("-last_activity")
