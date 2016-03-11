from . import querysets
from django.core import urlresolvers
from django.db import models
from django.utils import text, timezone
from entities import models as entities_models


class Image(models.Model):
    content = models.ForeignKey('Content')
    image = models.ImageField()


class Base(models.Model):
    author = models.ForeignKey('entities.Gestalt')
    date_created = models.DateTimeField(default=timezone.now)
    text = models.TextField('Text', blank=True)

    class Meta:
        abstract = True
        ordering = ('-date_created',)


class Comment(Base):
    content = models.ForeignKey('Content')


class Content(Base):
    subclass_names = ['Article', 'Event', 'Gallery']

    groups = models.ManyToManyField('entities.Group', through='entities.GroupContent')
    public = models.BooleanField('Veröffentlichen', default=False,
            help_text='Veröffentlichter Inhalt wird im öffentlichen Blog '
            'angezeigt, Benachrichtigungen werden an Gruppenmitglieder und '
            'Beobachterinnen versendet. Nicht veröffentlichter Inhalt ist nur '
            'gruppenintern zugänglich, Benachrichtigungen werden nur an '
            'Mitglieder versendet.')
    slug = models.SlugField(unique=True)
    title = models.CharField('Titel / Betreff', max_length=255)

    objects = models.Manager.from_queryset(querysets.ContentQuerySet)()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        try:
            return urlresolvers.reverse('group-content', args=[self.groups.first().slug, self.slug])
        except AttributeError:
            return urlresolvers.reverse('content', args=[self.author.user.username, self.slug])

    def get_display_type_name(self):
        return self.get_subclass_instance().display_type_name

    def get_subclass_instance(self):
        import sys
        for subclass_name in self.subclass_names:
            try:
                return getattr(self, subclass_name.lower())
            except getattr(sys.modules[__name__], subclass_name).DoesNotExist:
                pass


class Article(Content):
    display_type_name = 'Artikel'
    

class Event(Content):
    display_type_name = 'Ereignis'

    place = models.CharField(max_length=255)
    time = models.DateTimeField()

    objects = models.Manager.from_queryset(querysets.EventQuerySet)()

    class Meta:
        ordering = ('time',)

    def date(self):
        return self.time.date()

    def preview(self):
        return '{:%R} {}'.format(self.time, self.title)


class Gallery(Content):
    display_type_name = 'Galerie'
