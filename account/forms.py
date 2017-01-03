"""
This file is part of stadtgestalten.

stadtgestalten is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

stadtgestalten is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero Public License for more details.

You should have received a copy of the GNU Affero Public License
along with stadtgestalten.  If not, see <http://www.gnu.org/licenses/>.
"""

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


class LoginForm(util_forms.FormMixin, allauth.account.forms.LoginForm):
    layout = (
        layout.Div(
            'login',
            'password',
            'remember',
            util_forms.Submit('Anmelden'),
        ),
        layout.Div(
            layout.HTML(
                '<a class="btn btn-link" href="{{ signup_url }}">Konto anlegen</a>'
                '<a class="btn btn-link" '
                'href="{% url \'account_reset_password\' %}">Passwort vergessen</a>'
            ),
            css_class="account-actions",
        )
    )
    password = forms.CharField(label='Kennwort', widget=forms.PasswordInput())
    remember = forms.BooleanField(label='Anmeldung merken', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'] = forms.CharField(label='E-Mail-Adresse oder Pseudonym')
        self.helper.form_class += " form-login form-modern"


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
