import allauth.account
import allauth.account.forms
import allauth.account.adapter
import allauth.account.utils
from crispy_forms import layout
from django import forms
from django.contrib import auth
from utils import forms as util_forms


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


class PasswordReset(util_forms.FormMixin, allauth.account.forms.ResetPasswordForm):
    layout = (
            layout.HTML('<p>Wenn Du Dein Kennwort vergessen hast, gib bitte Deine '
                        'E-Mail-Adresse ein. Du erhältst dann eine Nachricht mit einem '
                        'Verweis zum Zurücksetzen des Kennworts an diese Adresse.</p>'),
            layout.Field('email', placeholder=''),
            util_forms.Submit('Kennwort zurücksetzen')
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = 'E-Mail-Adresse'


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
