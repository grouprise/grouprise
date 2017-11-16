import allauth
import django
from allauth.account import views
from crispy_forms import layout
from django.contrib import messages
from django.views import generic
from django.views.generic import edit as edit_views
from core import views as utils_views
from . import forms


class Confirm(utils_views.ActionMixin, edit_views.FormMixin, views.ConfirmEmailView):
    action = 'E-Mail-Adresse bestätigen'
    ignore_base_templates = True
    layout = layout.HTML('<p>Ist <a href="mailto:{{ confirmation.email_address.email }}">'
                         '{{ confirmation.email_address.email }}</a> eine E-Mail-Adresse des '
                         'Benutzers <em>{{ confirmation.email_address.user }}</em>?</p>')
    permission_required = 'account.confirm'

    def get_context_data(self, **kwargs):
        # as FormMixin doesn't call get_context_data() on super() we have to call it explicitly
        return views.ConfirmEmailView.get_context_data(self, **super().get_context_data(**kwargs))

    def get_parent(self):
        return self.get_redirect_url()


class Email(utils_views.ActionMixin, views.EmailView):
    form_class = forms.Email
    permission_required = 'account.email'
    title = 'E-Mail-Adressen'

    def get_parent(self):
        return self.request.user.gestalt


class Logout(utils_views.ActionMixin, edit_views.FormMixin, views.LogoutView):
    action = 'Abmelden'
    ignore_base_templates = True
    layout = layout.HTML('<p>Möchtest Du Dich abmelden?</p>')
    permission_required = 'account.logout'

    def get_parent(self):
        return self.request.user.gestalt


class PasswordChange(utils_views.ActionMixin, views.PasswordChangeView):
    action = 'Kennwort ändern'
    form_class = forms.PasswordChange
    ignore_base_templates = True
    permission_required = 'account.change_password'

    def get_parent(self):
        return self.request.user.gestalt


class PasswordReset(utils_views.ActionMixin, views.PasswordResetView):
    action = 'Kennwort zurücksetzen'
    form_class = forms.PasswordReset
    ignore_base_templates = True
    permission_required = 'account.reset_password'

    def get_context_data(self, **kwargs):
        kwargs['login_url'] = allauth.account.utils.passthrough_next_redirect_url(
                self.request, django.core.urlresolvers.reverse('login'),
                self.redirect_field_name)
        return django.views.generic.FormView.get_context_data(self, **kwargs)


class PasswordResetDone(generic.RedirectView):
    pattern_name = 'index'

    def get(self, request, *args, **kwargs):
        messages.info(request, 'Es wurde eine E-Mail an die angegebene Adresse versendet.')
        return super().get(request, *args, **kwargs)


class PasswordResetFromKey(utils_views.ActionMixin, views.PasswordResetFromKeyView):
    action = 'Kennwort ändern'
    form_class = forms.PasswordResetFromKey
    permission_required = 'account.reset_password'


class PasswordSet(utils_views.ActionMixin, views.PasswordSetView):
    action = 'Kennwort setzen'
    form_class = forms.PasswordSet
    ignore_base_templates = True
    permission_required = 'account.set_password'


class Signup(utils_views.ActionMixin, views.SignupView):
    action = 'Registrieren'
    form_class = forms.SignupForm
    ignore_base_templates = True
    # parent = 'gestalt-index'
    permission_required = 'account.signup'

    def get_context_data(self, **kwargs):
        kwargs['login_url'] = allauth.account.utils.passthrough_next_redirect_url(
                self.request, django.core.urlresolvers.reverse('login'),
                self.redirect_field_name)
        return django.views.generic.FormView.get_context_data(self, **kwargs)

    def get_success_url(self):
        return views.LoginView.get_success_url(self)
