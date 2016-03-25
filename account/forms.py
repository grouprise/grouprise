from allauth.account import forms as allauth_forms
from crispy_forms import layout
from django import forms
from util import forms as util_forms

class LoginForm(util_forms.FormMixin, allauth_forms.LoginForm):
    layout = (
            'login', 
            'password', 
            'remember', 
            util_forms.Submit('Anmelden'),
            layout.HTML('<p style="margin-top:13px;">'
                '<a href="#">Kennwort vergessen</a> | '
                '<a href="{{ signup_url }}">Registrieren</a></p>')
            )
    password = forms.CharField(label='Kennwort', widget=forms.PasswordInput())
    remember = forms.BooleanField(label='Anmeldung merken', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'] = forms.CharField(
                label='E-Mail-Adresse oder Pseudonym', 
                widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))
