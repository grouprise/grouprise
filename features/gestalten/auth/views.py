import allauth
import django
from django.views import generic

from . import forms
from allauth.account import views
from crispy_forms import layout
from django.contrib import messages
from django.views.generic import edit as edit_views
from core import views as utils_views


class Login(allauth.account.views.LoginView):
    permission_required = 'gestalten.login'
    form_class = forms.Login
    template_name = 'gestalten/login.html'

    def has_facebook_app(self):
        providers = allauth.socialaccount.providers.registry.get_list()
        for provider in providers:
            if provider.id == 'facebook' and provider.get_app(self.request):
                return True
        return False


class Logout(utils_views.ActionMixin, edit_views.FormMixin, views.LogoutView):
    action = 'Abmelden'
    ignore_base_templates = True
    layout = layout.HTML('<p>Möchtest Du Dich abmelden?</p>')
    permission_required = 'account.logout'

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
