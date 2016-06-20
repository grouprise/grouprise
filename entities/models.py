from . import querysets
from django.conf import settings
from django.contrib.contenttypes import fields, models as contenttype_models
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core import exceptions, urlresolvers, validators
from django.db import models
import randomcolor
from utils import text

def get_random_color():
    return randomcolor.RandomColor().generate(luminosity='dark')[0]


class Attention(models.Model):
    attendee = models.ForeignKey('Gestalt')
    content_type = models.ForeignKey(contenttype_models.ContentType)
    object_id = models.PositiveIntegerField()
    attended_object = fields.GenericForeignKey()


class Gestalt(models.Model):
    about = models.TextField('Selbstauskunft', blank=True)
    addressed_content = models.ManyToManyField('content.Content', related_name='gestalten', through='GestaltContent')
    avatar = models.ImageField(blank=True)
    background = models.ImageField('Hintergrundbild', blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    
    def __str__(self):
        name = ' '.join(filter(None, [self.user.first_name, self.user.last_name]))
        return name if name else self.user.username

    def get_absolute_url(self):
        return urlresolvers.reverse('gestalt', args=[type(self).objects.get(pk=self.pk).user.username])

class GestaltContent(models.Model):
    content = models.OneToOneField('content.Content')
    gestalt = models.ForeignKey('Gestalt')


def validate_reservation(value):
    if value in ['gestalt', 'stadt']:
        raise exceptions.ValidationError('Die Adresse \'%(value)s\' darf nicht verwendet werden.', params={'value': value}, code='reserved')


class AutoSlugField(models.SlugField):
    def __init__(self, *args, **kwargs):
        self.populate_from = kwargs.pop('populate_from')
        self.reserve = kwargs.pop('reserve')
        kwargs['validators'] = [validate_reservation]
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs['populate_from'] = self.populate_from
        kwargs['reserve'] = self.reserve
        return name, path, args, kwargs

    def pre_save(self, model_instance, add):
        if add:
            value = text.slugify(type(model_instance), self.attname, getattr(model_instance, self.populate_from), validate_reservation)
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super().pre_save(model_instance, add)


class Group(models.Model):
    address = models.TextField('Anschrift', blank=True)
    attendees = models.ManyToManyField('Gestalt', related_name='attended_groups', through='GroupAttention')
    avatar = models.ImageField(blank=True)
    avatar_color = models.CharField(max_length=7, default=get_random_color)
    content = models.ManyToManyField('content.Content', related_name='groups', through='GroupContent')
    date_created = models.DateField(auto_now_add=True)
    date_founded = models.DateField('Gruppe gegründet', null=True, blank=True)
    logo = models.ImageField(blank=True)
    members = models.ManyToManyField('Gestalt', related_name='groups', through='Membership')
    name = models.CharField('Name', max_length=255)
    slug = AutoSlugField('Adresse der Gruppenseite', populate_from='name', reserve=['gestalt', 'stadt'], unique=True)
    url = models.URLField('Adresse im Web', blank=True)
    description = models.TextField('Kurzbeschreibung', blank=True, default='', max_length=200)

    objects = models.Manager.from_queryset(querysets.Group)()

    class Meta:
        # FIXME: we should use case-insensitive ordering here
        # https://code.djangoproject.com/ticket/26257
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return urlresolvers.reverse('group', args=[type(self).objects.get(pk=self.pk).slug])

    def get_head_gallery(self):
        return self.content.exclude(gallery=None).filter(public=True, groupcontent__pinned=True).first()

    def get_initials(self):
        import re
        initials = ''
        for w in self.name.split():
            m = re.search('[a-zA-Z0-9]', w)
            initials += m.group(0) if m else ''
        return initials
    

class GroupAttention(models.Model):
    attendee = models.ForeignKey('Gestalt')
    group = models.ForeignKey('Group')

class GroupContent(models.Model):
    content = models.OneToOneField('content.Content')
    group = models.ForeignKey('Group')
    pinned = models.BooleanField(default=False)

class Membership(models.Model):
    date_joined = models.DateField(auto_now_add=True)
    gestalt = models.ForeignKey('Gestalt')
    group = models.ForeignKey('Group')

    class Meta:
        unique_together = ('gestalt', 'group')
