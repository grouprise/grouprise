import allauth
from crispy_forms import layout
from django import forms
from django.contrib import auth
from django.core.exceptions import ValidationError

from core import forms as util_forms
from features.gestalten import models
from features.stadt.forms import validate_entity_slug

username_validators = [validate_entity_slug]


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
        gestalt = models.Gestalt.objects.get_or_create_by_email(value)
        if gestalt.can_login():
            raise ValidationError(self.error_messages['login'], code='login')
        return gestalt


class Create(util_forms.FormMixin, allauth.account.forms.SignupForm):
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


class Update(forms.ModelForm):
    class Meta:
        model = models.Gestalt
        fields = ('about', 'public')
        widgets = {'about': forms.Textarea({'rows': 5})}

    first_name = forms.CharField(label='Vorname', required=False)
    last_name = forms.CharField(label='Nachname', required=False)
    slug = forms.SlugField(
            label='Pseudonym', help_text='Nur Buchstaben, Ziffern, Unter- und Bindestriche. '
            'Keine Umlaute, ß oder andere Sonderzeichen.')

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        validate_entity_slug(slug, self.instance)
        return slug

    def get_instance(self):
        return self.instance.user

    def save(self, commit=True):
        self.instance.user.first_name = self.cleaned_data['first_name']
        self.instance.user.last_name = self.cleaned_data['last_name']
        self.instance.user.username = self.cleaned_data['slug']
        if commit:
            self.instance.user.save()
        return super().save(commit)


class UpdateEmail(util_forms.FormMixin, allauth.account.forms.AddEmailForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = 'E-Mail-Adresse'
        del self.fields['email'].widget.attrs['placeholder']


class UpdatePassword(allauth.account.forms.ChangePasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['oldpassword'].label = 'Aktuelles Kennwort'
        self.fields['password1'].label = 'Neues Kennwort'
        self.fields['password2'].label = 'Neues Kennwort (Wiederholung)'
        del self.fields['oldpassword'].widget.attrs['placeholder']
        del self.fields['password1'].widget.attrs['placeholder']
        del self.fields['password2'].widget.attrs['placeholder']


class UpdatePasswordSet(util_forms.FormMixin, allauth.account.forms.SetPasswordForm):
    layout = (
            layout.Field('password1', placeholder=''),
            layout.Field('password2', placeholder=''),
            util_forms.Submit('Kennwort setzen')
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Kennwort'
        self.fields['password2'].label = 'Kennwort (Wiederholung)'


class UpdatePasswordKey(util_forms.FormMixin, allauth.account.forms.ResetPasswordKeyForm):
    layout = (
            layout.Field('password1', placeholder=''),
            layout.Field('password2', placeholder=''),
            util_forms.Submit('Kennwort ändern')
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Kennwort'
        self.fields['password2'].label = 'Kennwort (Wiederholung)'
