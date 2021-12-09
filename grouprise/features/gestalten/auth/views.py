import allauth
import django
from allauth.account import views
from django.contrib import messages
from django.views import generic

from grouprise.core.views import PermissionMixin

from . import forms


class Login(PermissionMixin, allauth.account.views.LoginView):
    permission_required = "gestalten.login"
    form_class = forms.Login
    template_name = "auth/login.html"

    def has_facebook_app(self):
        providers = allauth.socialaccount.providers.registry.get_list()
        for provider in providers:
            if provider.id == "facebook" and provider.get_app(self.request):
                return True
        return False


class Logout(PermissionMixin, views.LogoutView):
    permission_required = "account.logout"
    template_name = "auth/logout.html"

    def get_parent(self):
        return self.request.user.gestalt


class PasswordReset(PermissionMixin, views.PasswordResetView):
    permission_required = "account.reset_password"
    form_class = forms.PasswordReset
    template_name = "auth/password_reset.html"

    def get_context_data(self, **kwargs):
        kwargs["login_url"] = allauth.account.utils.passthrough_next_redirect_url(
            self.request, django.urls.reverse("account_login"), self.redirect_field_name
        )
        return django.views.generic.FormView.get_context_data(self, **kwargs)


class PasswordResetDone(generic.RedirectView):
    pattern_name = "index"

    def get(self, request, *args, **kwargs):
        messages.info(
            request, "Es wurde eine E-Mail an die angegebene Adresse versendet."
        )
        return super().get(request, *args, **kwargs)
