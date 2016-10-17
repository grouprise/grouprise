from allauth.account import adapter as allauth_adapter
from django.conf import settings
from django.contrib import auth
from django.core import exceptions, urlresolvers
from django.db import models
from features.memberships import models as memberships
import randomcolor
from utils import text


def get_random_color():
    return randomcolor.RandomColor().generate(luminosity='dark')[0]


class Gestalt(models.Model):
    about = models.TextField('Selbstauskunft', blank=True)
    addressed_content = models.ManyToManyField(
            'content.Content', related_name='gestalten', through='GestaltContent')
    avatar = models.ImageField(blank=True)
    avatar_color = models.CharField(max_length=7, default=get_random_color)
    background = models.ImageField('Hintergrundbild', blank=True)
    public = models.BooleanField(
            'Benutzerseite veröffentlichen',
            default=False,
            help_text='Meine Benutzerseite ist für alle Besucherinnen sichtbar.'
            )
    user = models.OneToOneField(settings.AUTH_USER_MODEL)

    @staticmethod
    def get_or_create(email):
        user, created = auth.get_user_model().objects.get_or_create(
                email=email)
        if created:
            allauth_adapter.get_adapter().populate_username(None, user)
            user.set_unusable_password()
            user.save()
        return user.gestalt

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
        return urlresolvers.reverse('gestalt-message-create', args=(self.pk,))

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


class GestaltContent(models.Model):
    content = models.OneToOneField('content.Content')
    gestalt = models.ForeignKey('Gestalt')


# FIXME: can be deleted after sqashing migrations
def validate_reservation(value):
    if value in ['gestalt', 'stadt']:
        raise exceptions.ValidationError(
                "Die Adresse \'%(value)s\' darf nicht verwendet werden.", params={'value': value},
                code='reserved')


# FIXME: can be deleted after sqashing migrations
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
            value = text.slugify(
                type(model_instance), self.attname, getattr(model_instance, self.populate_from),
                validate_reservation)
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super().pre_save(model_instance, add)


class GroupContent(models.Model):
    content = models.OneToOneField('content.Content')
    group = models.ForeignKey('groups.Group')
    pinned = models.BooleanField(default=False)

    def is_external(self):
        return not memberships.Membership.objects.filter(
                group=self.group, member=self.content.author
                ).exists()
