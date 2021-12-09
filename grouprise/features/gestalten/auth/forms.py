import allauth
import allauth.account
import allauth.account.adapter
import allauth.account.forms
import allauth.account.utils
from django import forms


class Login(allauth.account.forms.LoginForm):
    password = forms.CharField(label="Kennwort", widget=forms.PasswordInput())
    remember = forms.BooleanField(label="Anmeldung merken", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["login"] = forms.CharField(
            label="E-Mail-Adresse oder Pseudonym",
            widget=forms.TextInput(
                attrs={
                    "autofocus": "autofocus",
                    "autocomplete": "username",
                    "autocorrect": "off",
                    "autocapitalize": "none",
                    "spellcheck": "false",
                }
            ),
        )


class PasswordReset(allauth.account.forms.ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].label = "E-Mail-Adresse"
