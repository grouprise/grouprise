import allauth
from crispy_forms import layout
from django import forms

import allauth.account
import allauth.account.forms
import allauth.account.adapter
import allauth.account.utils
from core import forms as util_forms


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
