from . import querysets
import core.models
from django.conf import settings
from django.contrib.contenttypes import fields
from django.contrib.sites import models as sites_models
from django.core import mail, urlresolvers
from django.db import models
from django.utils import timezone
from email import utils as email_utils


class Image(models.Model):
    content = models.ForeignKey('Content', blank=True, null=True, related_name='images')
    file = models.ImageField('Datei')
    weight = models.PositiveSmallIntegerField(default=0)
    creator = models.ForeignKey('entities.Gestalt', related_name='+', null=True, blank=True)

    class Meta:
        ordering = ('weight',)


class Base(core.models.Model):
    author = models.ForeignKey(
            'entities.Gestalt',
            related_name='authored_%(class)s')
    date_created = models.DateTimeField(default=timezone.now)
    text = models.TextField('Text')

    class Meta:
        abstract = True
        ordering = ('-date_created',)

    def is_reply(self):
        return False

    def notify(self, gestalten):
        groups = self.get_content().groups.all()
        for recipient in gestalten:
            if recipient.user.email:
                to = '{} <{}>'.format(recipient, recipient.user.email)
                body = '{text}\n\n-- \nAntworten und weitere Möglichkeiten:\n{protocol}://{domain}{path}'.format(
                        domain=sites_models.Site.objects.get_current().domain,
                        path=self.get_content().get_absolute_url(),
                        protocol=settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL,
                        text=self.text,
                        )
                slugs = [g.slug for g in groups]
                subject = '{reply}{groups}{title}'.format(
                        reply='Re: ' if self.is_reply() else '',
                        groups='[{}] '.format(','.join(slugs)) if groups else '',
                        title=self.get_content().title
                        )
                from_email = '{gestalt} via {site} <{email}>'.format(
                        gestalt=self.author,
                        site=sites_models.Site.objects.get_current().name,
                        email=settings.DEFAULT_FROM_EMAIL
                        )
                date = email_utils.formatdate(localtime=True)
                message = mail.EmailMessage(body=body, from_email=from_email,
                        subject=subject, to=[to], headers={'Date': date})
                message.send()


class Comment(Base):
    content = models.ForeignKey('Content', related_name='comments')

    class Meta:
        ordering = ('date_created',)

    def get_content(self):
        return self.content

    def is_reply(self):
        return True


class Content(Base):
    subclass_names = ['Article', 'Event', 'Gallery']

    comment_authors = models.ManyToManyField('entities.Gestalt', through='Comment')
    public = models.BooleanField(
            'Veröffentlichen',
            default=False,
            help_text='Veröffentlichte Beiträge sind auch für Besucherinnen '
            'sichtbar, die nicht Mitglied der Gruppe sind.'
            )
    slug = models.SlugField(default=None, null=True, unique=True)
    title = models.CharField('Titel', max_length=255)

    objects = models.Manager.from_queryset(querysets.ContentQuerySet)()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if not self.public:
            return urlresolvers.reverse('internal-content', args=[self.pk])
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

    def get_content(self):
        return self.get_subclass_instance()

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


class Article(Content):
    objects = models.Manager.from_queryset(querysets.ContentQuerySet)()

    def get_display_type_name(self):
        return 'Artikel' if self.public else 'Gespräch'


class Event(Content):
    place = models.CharField('Ort / Anschrift', max_length=255)
    time = models.DateTimeField('Datum / Uhrzeit')

    objects = models.Manager.from_queryset(querysets.EventQuerySet)()

    class Meta:
        ordering = ('time',)

    def date(self):
        return self.time.date()

    def get_display_type_name(self):
        return 'Ereignis' if self.public else 'Internes Ereignis'


class Gallery(Content):
    objects = models.Manager.from_queryset(querysets.ContentQuerySet)()

    def get_display_type_name(self):
        return 'Galerie' if self.public else 'Interne Galerie'
