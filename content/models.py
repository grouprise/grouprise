from . import querysets
from django.conf import settings
from django.contrib.sites import models as sites_models
from django.core import mail, urlresolvers
from django.db import models
from django.utils import timezone


class Image(models.Model):
    content = models.ForeignKey('Content')
    image = models.ImageField()


class Base(models.Model):
    author = models.ForeignKey(
            'entities.Gestalt',
            related_name='authored_%(class)s')
    date_created = models.DateTimeField(default=timezone.now)
    text = models.TextField('Text', blank=True)

    class Meta:
        abstract = True
        ordering = ('-date_created',)


class Comment(Base):
    content = models.ForeignKey('Content')


class Content(Base):
    subclass_names = ['Article', 'Event', 'Gallery']

    public = models.BooleanField(
            'Veröffentlichen',
            default=False,
            help_text='Veröffentlichte Beiträge sind auch für Besucherinnen '
            'sichtbar, die nicht Mitglied der Gruppe sind.'
            )
    slug = models.SlugField(unique=True)
    title = models.CharField('Titel', max_length=255)

    objects = models.Manager.from_queryset(querysets.ContentQuerySet)()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        try:
            return urlresolvers.reverse(
                    'content',
                    args=[self.groups.first().slug, self.slug]
                    )
        except AttributeError:
            return urlresolvers.reverse(
                    'gestalt-content',
                    args=[self.author.user.username, self.slug]
                    )

    def get_display_type_name(self):
        return self.get_subclass_instance().get_display_type_name()

    def get_subclass_instance(self):
        import sys
        for subclass_name in self.subclass_names:
            try:
                return getattr(self, subclass_name.lower())
            except getattr(sys.modules[__name__], subclass_name).DoesNotExist:
                pass

    def get_type_name(self):
        return self.get_subclass_instance()._meta.model_name

    def notify(self, gestalten):
        for recipient in gestalten:
            if recipient.user.email:
                to = '{} <{}>'.format(recipient, recipient.user.email)
                body = '{text}\n\n-- \n{protocol}://{domain}{path}'.format(
                        domain=sites_models.Site.objects.get_current().domain,
                        path=self.get_absolute_url(),
                        protocol=settings.HTTP_PROTOCOL,
                        text=self.text,
                        )
                message = mail.EmailMessage(body=body, to=[to])
                message.subject = self.title
                message.send()


class Article(Content):
    objects = models.Manager.from_queryset(querysets.ContentQuerySet)()

    def get_display_type_name(self):
        return 'Artikel' if self.public else 'Interne Nachricht'


class Event(Content):
    place = models.CharField('Ort', max_length=255)
    time = models.DateTimeField('Datum / Uhrzeit')

    objects = models.Manager.from_queryset(querysets.EventQuerySet)()

    class Meta:
        ordering = ('time',)

    def date(self):
        return self.time.date()

    def get_display_type_name(self):
        return 'Ereignis' if self.public else 'Internes Ereignis'

    def preview(self):
        return '{:%R} {}'.format(self.time, self.title)


class Gallery(Content):
    objects = models.Manager.from_queryset(querysets.ContentQuerySet)()

    def get_display_type_name(self):
        return 'Galerie' if self.public else 'Interne Galerie'
