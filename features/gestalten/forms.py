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
import allauth.account
import allauth.account.forms
import allauth.account.adapter
import allauth.account.utils
from django.contrib import auth
from core import forms as util_forms


class Email(util_forms.FormMixin, allauth.account.forms.AddEmailForm):
    layout = (
            layout.Field('email', placeholder=''),
            util_forms.Submit('E-Mail-Adresse hinzufügen', 'action_add'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = 'E-Mail-Adresse'


class PasswordChange(util_forms.FormMixin, allauth.account.forms.ChangePasswordForm):
    layout = (
            layout.Field('oldpassword', placeholder=''),
            layout.Field('password1', placeholder=''),
            layout.Field('password2', placeholder=''),
            util_forms.Submit('Kennwort ändern')
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['oldpassword'].label = 'Aktuelles Kennwort'
        self.fields['password1'].label = 'Neues Kennwort'
        self.fields['password2'].label = 'Neues Kennwort (Wiederholung)'


class PasswordSet(util_forms.FormMixin, allauth.account.forms.SetPasswordForm):
    layout = (
            layout.Field('password1', placeholder=''),
            layout.Field('password2', placeholder=''),
            util_forms.Submit('Kennwort setzen')
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Kennwort'
        self.fields['password2'].label = 'Kennwort (Wiederholung)'


class PasswordResetFromKey(util_forms.FormMixin, allauth.account.forms.ResetPasswordKeyForm):
    layout = (
            layout.Field('password1', placeholder=''),
            layout.Field('password2', placeholder=''),
            util_forms.Submit('Kennwort ändern')
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Kennwort'
        self.fields['password2'].label = 'Kennwort (Wiederholung)'


class SignupForm(util_forms.FormMixin, allauth.account.forms.SignupForm):
    layout = (
            layout.HTML(
                '<p>'
                'Benutzerkonto schon vorhanden? <a href="{{ login_url }}">Melde Dich an.</a>'
                '</p>'
                '<div class="disclaimer content-block">'
                '<p>'
                'Deine E-Mail Adresse wird nicht weitergegeben und auch nicht auf der Seite '
                'angezeigt. Sie wird dazu genutzt Dir Benachrichtungen zu schicken.'
                '</p>'
                '</div>'
            ),
            'email',
            'password1',
            'password2',
            util_forms.Submit('Registrieren'),
            )
    password1 = forms.CharField(label='Kennwort', widget=forms.PasswordInput())
    password2 = forms.CharField(label='Kennwort (Wiederholung)', widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'] = forms.EmailField(label='E-Mail-Adresse')

    def clean_email(self):
        try:
            return super().clean_email()
        except forms.ValidationError as e:
            try:
                user = auth.get_user_model().objects.get(email=self.cleaned_data['email'])
                if user.has_usable_password():
                    raise e
            except auth.get_user_model().DoesNotExist:
                raise e
        return self.cleaned_data['email']

    def save(self, request):
        try:
            adapter = allauth.account.adapter.get_adapter(request)
            user = auth.get_user_model().objects.get(email=self.cleaned_data['email'])
            adapter.set_password(user, self.cleaned_data["password1"])
            allauth.account.utils.setup_user_email(request, user, [])
            return user
        except auth.get_user_model().DoesNotExist:
            return super().save(request)


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
