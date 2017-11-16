import allauth
import django
from crispy_forms import bootstrap, layout
from django import forms
from django.contrib.auth import models as auth_models
from django.contrib.sites import models as sites_models
from django.core.exceptions import ValidationError

from features.groups.models import Group
from features.gestalten import models
from core import forms as utils_forms


class GestaltByEmailField(forms.EmailField):
    default_error_messages = {
        'login': 'Es gibt bereits ein Benutzerkonto mit dieser E-Mail-Adresse. Bitte melde '
                 'Dich mit E-Mail-Adresse und Kennwort an.'
    }

    def __init__(self, *args, **kwargs):
        del kwargs['limit_choices_to']
        del kwargs['queryset']
        del kwargs['to_field_name']
        super().__init__(*args, **kwargs)

    def clean(self, value):
        value = super().clean(value)
        gestalt = models.Gestalt.get_or_create(value)
        if gestalt.can_login():
            raise ValidationError(self.error_messages['login'], code='login')
        return gestalt


def validate_slug(slug):
    if slug in django.conf.settings.ENTITY_SLUG_BLACKLIST:
        raise django.core.exceptions.ValidationError(
                'Die Adresse \'%(slug)s\' ist reserviert und darf nicht verwendet werden.',
                params={'slug': slug}, code='reserved')
    if (Group.objects.filter(slug__iexact=slug).exists()
            or models.Gestalt.objects.filter(user__username__iexact=slug).exists()):
        raise django.core.exceptions.ValidationError(
                'Die Adresse \'%(slug)s\' ist bereits vergeben.',
                params={'slug': slug}, code='in-use')


class User(utils_forms.FormMixin, forms.ModelForm):
    class Meta:
        fields = ('first_name', 'last_name', 'username')
        labels = {'username': 'Adresse der Benutzerseite / Pseudonym'}
        model = auth_models.User

    def clean_username(self):
        slug = self.cleaned_data['username']
        validate_slug(slug)
        return slug


class Gestalt(utils_forms.ExtraFormMixin, forms.ModelForm):
    extra_form_class = User

    class Meta:
        fields = ('about', 'public')
        model = models.Gestalt

    def get_instance(self):
        return self.instance.user

    def get_layout(self):
        DOMAIN = sites_models.Site.objects.get_current().domain
        return (
                bootstrap.PrependedText(
                    'username',
                    '%(domain)s/' % {'domain': DOMAIN}),
                'first_name',
                'last_name',
                layout.Field('about', rows=5),
                'public',
                utils_forms.Submit('Profil ändern'),
                )


class Login(allauth.account.forms.LoginForm):
    password = forms.CharField(label='Kennwort', widget=forms.PasswordInput())
    remember = forms.BooleanField(label='Anmeldung merken', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'] = forms.CharField(
                label='E-Mail-Adresse oder Pseudonym',
                widget=forms.TextInput(attrs={
                    'autofocus': 'autofocus',
                    'autocomplete': 'username',
                    'autocorrect': 'off',
                    'autocapitalize': 'none',
                    'spellcheck': 'false'
                }))
