import django.contrib.contenttypes.models
from allauth.account import adapter as allauth_adapter
from django.conf import settings
from django.contrib import auth
from django import urls
from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import SmartResize, Transpose

import core
from core import colors


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
            user, created = auth.get_user_model().objects.get_or_create(
                    email=email)
        if created:
            allauth_adapter.get_adapter().populate_username(None, user)
            user.set_unusable_password()
            user.save()
        return user.gestalt


class Gestalt(core.models.Model):
    is_group = False

    about = models.TextField('Selbstauskunft', blank=True)
    avatar = core.models.ImageField(blank=True)
    avatar_64 = ImageSpecField(
            source='avatar', processors=[Transpose(), SmartResize(64, 64)], format='PNG')
    avatar_color = models.CharField(max_length=7, default=colors.get_random_color)
    background = core.models.ImageField('Hintergrundbild', blank=True)
    background_cover = ImageSpecField(
            source='background', processors=[Transpose(), SmartResize(1140, 456)],
            format='JPEG')
    public = models.BooleanField(
            'Benutzerseite veröffentlichen',
            default=False,
            help_text='Öffentliche Benutzerseiten sind für alle Besucherinnen sichtbar.'
            )
    score = models.IntegerField(default=0)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    associations = django.contrib.contenttypes.fields.GenericRelation(
            'associations.Association', content_type_field='entity_type',
            object_id_field='entity_id', related_query_name='gestalt')

    objects = models.Manager.from_queryset(GestaltQuerySet)()

    @property
    def name(self):
        return ' '.join(filter(None, [self.user.first_name, self.user.last_name]))

    @property
    def slug(self):
        return self.user.username

    def __str__(self):
        return self.name or self.slug

    def can_login(self):
        return self.user.has_usable_password()

    def delete(self, *args, **kwargs):
        data = self.get_data()
        unknown_gestalt = Gestalt.objects.get(id=settings.GROUPRISE.get('UNKNOWN_GESTALT_ID', 1))
        data['associations'].update(entity_id=unknown_gestalt.id)
        data['contributions'].update(author=unknown_gestalt)
        data['images'].update(creator=unknown_gestalt)
        data['memberships_created'].update(created_by=unknown_gestalt)
        data['versions'].update(author=unknown_gestalt)
        data['votes'].update(voter=unknown_gestalt)
        self.user.delete()

    def get_absolute_url(self):
        if self.public:
            return self.get_profile_url()
        else:
            return self.get_contact_url()

    def get_absolute_url_for_user(self, user):
        if user and user.has_perm('gestalten.view', self):
            return self.get_profile_url()
        else:
            return self.get_contact_url()

    def get_contact_url(self):
        return urls.reverse('create-gestalt-conversation', args=(self.pk,))

    def get_data(self):
        '''
        Return all data directly related to this gestalt. May be used e.g. in conjunction with
        deleting users.
        '''
        data = {}
        data['gestalt'] = self
        data['user'] = self.user

        # data['groups_created'] = ?
        data['memberships'] = self.memberships
        data['subscriptions'] = self.subscriptions
        data['tokens'] = self.permissiontoken_set
        data['settings'] = self.gestaltsetting_set

        data['associations'] = self.associations
        data['contributions'] = self.contributions
        data['images'] = self.images
        data['memberships_created'] = self.memberships_created
        data['versions'] = self.versions
        data['votes'] = self.votes
        return data

    def get_profile_url(self):
        return urls.reverse(
                'entity', args=[type(self).objects.get(pk=self.pk).user.username])

    # FIXME: move to template filter
    def get_initials(self):
        import re
        initials = ''
        for w in str(self).split():
            m = re.search('[a-zA-Z0-9]', w)
            initials += m.group(0) if m else ''
        return initials


class GestaltSetting(models.Model):
    class Meta:
        unique_together = ('gestalt', 'category', 'name')

    gestalt = models.ForeignKey('gestalten.Gestalt', on_delete=models.CASCADE)
    category = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=255)
    value = models.TextField()
