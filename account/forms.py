from allauth.account import adapter as allauth_adapter, forms as allauth_forms, utils as allauth_utils
from crispy_forms import layout
from django import forms
from django.contrib import auth
from utils import forms as util_forms


class Email(util_forms.FormMixin, allauth_forms.AddEmailForm):
    layout = (
            layout.Field('email', placeholder=''),
            util_forms.Submit('E-Mail-Adresse hinzufügen', 'action_add'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = 'E-Mail-Adresse'


class LoginForm(util_forms.FormMixin, allauth_forms.LoginForm):
    layout = (
            layout.HTML('<p>Noch kein Benutzerkonto? '
                '<a href="{{ signup_url }}">Leg Dir eins an.</a></p>'),
            'login', 
            'password', 
            'remember', 
            util_forms.Submit('Anmelden'),
            layout.HTML('<p style="margin-top:13px;">'
                "<a href=\"{% url 'account_reset_password' %}\">Kennwort vergessen</a> | "
                '<a href="{{ signup_url }}">Registrieren</a></p>')
            )
    password = forms.CharField(label='Kennwort', widget=forms.PasswordInput())
    remember = forms.BooleanField(label='Anmeldung merken', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'] = forms.CharField(label='E-Mail-Adresse oder Pseudonym')


class PasswordChange(util_forms.FormMixin, allauth_forms.ChangePasswordForm):
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


class PasswordReset(util_forms.FormMixin, allauth_forms.ResetPasswordForm):
    layout = (
            layout.HTML('<p>Wenn Du Dein Kennwort vergessen hast, gib bitte Deine E-Mail-Adresse ein. Du erhälst dann eine Nachricht mit einem Verweis zum Zurücksetzen des Kennworts an diese Adresse.</p>'),
            layout.Field('email', placeholder=''),
            util_forms.Submit('Kennwort zurücksetzen')
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = 'E-Mail-Adresse'


class PasswordResetFromKey(util_forms.FormMixin, allauth_forms.ResetPasswordKeyForm):
    layout = (
            layout.Field('password1', placeholder=''),
            layout.Field('password2', placeholder=''),
            util_forms.Submit('Kennwort ändern')
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Kennwort'
        self.fields['password2'].label = 'Kennwort (Wiederholung)'


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
            adapter = allauth_adapter.get_adapter(request)
            user = auth.get_user_model().objects.get(email=self.cleaned_data['email'])
            adapter.set_password(user, self.cleaned_data["password1"])
            allauth_utils.setup_user_email(request, user, [])
            return user
        except auth.get_user_model().DoesNotExist:
            return super().save(request)
