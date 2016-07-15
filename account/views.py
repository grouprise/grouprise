from . import forms
from allauth.account import views
from crispy_forms import layout
from django.contrib import messages
from django.views import generic
from django.views.generic import edit as edit_views
from utils import views as utils_views

class Confirm(utils_views.ActionMixin, edit_views.FormMixin, views.ConfirmEmailView):
    action = 'E-Mail-Adresse bestätigen'
    ignore_base_templates = True
    layout = layout.HTML('<p>Ist <a href="mailto:{{ confirmation.email_address.email }}">{{ confirmation.email_address.email }}</a> eine E-Mail-Adresse des Benutzers <em>{{ confirmation.email_address.user }}</em>?</p>')
    permission = 'account.confirm'

    def get_context_data(self, **kwargs):
        # as FormMixin doesn't call get_context_data() on super() we have to call it explicitly
        return views.ConfirmEmailView.get_context_data(self, **super().get_context_data(**kwargs))

    def get_parent(self):
        return self.get_redirect_url()


class Email(utils_views.ActionMixin, views.EmailView):
    form_class = forms.Email
    permission = 'account.email'
    title = 'E-Mail-Adressen'

    def get_parent(self):
        return self.request.user.gestalt


class Login(utils_views.ActionMixin, views.LoginView):
    action = 'Anmelden'
    form_class = forms.LoginForm
    ignore_base_templates = True
    parent = 'gestalt-index'
    permission = 'account.login'

    def get_success_url(self):
        return views.LoginView.get_success_url(self)

class Logout(utils_views.ActionMixin, edit_views.FormMixin, views.LogoutView):
    action = 'Abmelden'
    ignore_base_templates = True
    layout = layout.HTML('<p>Möchtest Du Dich abmelden?</p>')
    permission = 'account.logout'

    def get_parent(self):
        return self.request.user.gestalt


class PasswordChange(utils_views.ActionMixin, views.PasswordChangeView):
    action = 'Kennwort ändern'
    form_class = forms.PasswordChange
    ignore_base_templates = True
    permission = 'account.change_password'
    
    def get_parent(self):
        return self.request.user.gestalt


class PasswordReset(utils_views.ActionMixin, views.PasswordResetView):
    action = 'Kennwort zurücksetzen'
    form_class = forms.PasswordReset
    ignore_base_templates = True
    permission = 'account.reset_password'


class PasswordResetDone(generic.RedirectView):
    pattern_name = 'index'

    def get(self, request, *args, **kwargs):
        messages.info(request, 'Es wurde eine E-Mail an die angegebene Adresse versendet.')
        return super().get(request, *args, **kwargs)


class PasswordResetFromKey(utils_views.ActionMixin, views.PasswordResetFromKeyView):
    action = 'Kennwort ändern'
    form_class = forms.PasswordResetFromKey
    permission = 'account.reset_password'


class Signup(utils_views.ActionMixin, views.SignupView):
    action = 'Registrieren'
    form_class = forms.SignupForm
    ignore_base_templates = True
    parent = 'gestalt-index'
    permission = 'account.signup'

    def get_success_url(self):
        return views.LoginView.get_success_url(self)
