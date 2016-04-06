from allauth.account import forms as allauth_forms
from crispy_forms import layout
from django import forms
from utils import forms as util_forms

class LoginForm(util_forms.FormMixin, allauth_forms.LoginForm):
    layout = (
            layout.HTML('<p>Noch kein Benutzerkonto? '
                '<a href="{{ signup_url }}">Leg Dir eins an.</a></p>'),
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
        self.fields['login'] = forms.CharField(label='E-Mail-Adresse oder Pseudonym')

class SignupForm(util_forms.FormMixin, allauth_forms.SignupForm):
    layout = (
            layout.HTML('<p>Benutzerkonto schon vorhanden? '
                '<a href="{{ login_url }}">Melde Dich an.</a></p>'),
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
