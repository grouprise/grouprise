import django.contrib.contenttypes.models
from django.conf import settings
from django.contrib import auth
from django.core import urlresolvers
from django.db import models
from allauth.account import adapter as allauth_adapter

from core import colors


class Gestalt(models.Model):
    is_group = False

    about = models.TextField('Selbstauskunft', blank=True)
    addressed_content = models.ManyToManyField(
            'content.Content', related_name='gestalten', through='entities.GestaltContent')
    avatar = models.ImageField(blank=True)
    avatar_color = models.CharField(max_length=7, default=colors.get_random_color)
    background = models.ImageField('Hintergrundbild', blank=True)
    public = models.BooleanField(
            'Benutzerseite veröffentlichen',
            default=False,
            help_text='Meine Benutzerseite ist für alle Besucherinnen sichtbar.'
            )
    score = models.IntegerField(default=0)
    user = models.OneToOneField(settings.AUTH_USER_MODEL)

    associations = django.contrib.contenttypes.fields.GenericRelation(
            'associations.Association', content_type_field='entity_type',
            object_id_field='entity_id', related_query_name='gestalt')

    @property
    def slug(self):
        return self.user.username

    @staticmethod
    def get_or_create(email):
        user, created = auth.get_user_model().objects.get_or_create(
                email=email)
        if created:
            allauth_adapter.get_adapter().populate_username(None, user)
            user.set_unusable_password()
            user.save()
        return user.gestalt

    @classmethod
    def get_content_type(cls):
        return django.contrib.contenttypes.models.ContentType.objects.get_for_model(cls)

    def __str__(self):
        name = ' '.join(filter(None, [self.user.first_name, self.user.last_name]))
        return name if name else self.user.username

    def can_login(self):
        return self.user.has_usable_password()

    def get_absolute_url(self):
        if self.public:
            return self.get_profile_url()
        else:
            return self.get_contact_url()

    def get_contact_url(self):
        return urlresolvers.reverse('create-gestalt-conversation', args=(self.pk,))

    def get_profile_url(self):
        return urlresolvers.reverse(
                'gestalt', args=[type(self).objects.get(pk=self.pk).user.username])

    # FIXME: move to template filter
    def get_initials(self):
        import re
        initials = ''
        for w in str(self).split():
            m = re.search('[a-zA-Z0-9]', w)
            initials += m.group(0) if m else ''
        return initials


class GestaltSetting(models.Model):
    gestalt = models.ForeignKey('gestalten.Gestalt', on_delete=models.CASCADE)
    category = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)
    value = models.TextField()
