import allauth
import django
from django.views import generic

import core
from core.views import base
from features.associations import models as associations
from . import forms, models
from allauth.account import views
from crispy_forms import layout
from django.contrib import messages
from django.views.generic import edit as edit_views
from core import views as utils_views


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


class Detail(
        core.views.PermissionMixin, django.views.generic.list.MultipleObjectMixin,
        django.views.generic.DetailView):
    permission_required = 'gestalten.view'
    model = models.Gestalt
    paginate_by = 10
    template_name = 'gestalten/detail.html'

    def get_context_data(self, **kwargs):
        associations = self.object.associations.ordered_user_content(self.request.user)
        return super().get_context_data(
                associations=associations,
                gestalt=self.object,
                object_list=associations,
                **kwargs)

    def get_object(self):
        return self.object


class List(base.PermissionMixin, generic.ListView):
    permission_required = 'gestalten.view_list'
    queryset = models.Gestalt.objects.filter(public=True)
    ordering = ['-score', '-user__date_joined']
    paginate_by = 10
    template_name = 'gestalten/list.html'

    def get_content(self):
        return associations.Association.objects.filter(
                entity_type=models.Gestalt.content_type).can_view(self.request.user)


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


class Update(core.views.ActionMixin, django.views.generic.UpdateView):
    action = 'Dein Profil'
    form_class = forms.Gestalt
    menu = 'gestalt'
    message = 'Die Einstellungen wurden geändert.'
    model = models.Gestalt
    permission_required = 'entities.change_gestalt'

    def get_object(self):
        return self.request.user.gestalt

    def get_parent(self):
        return self.object

    def get_success_url(self):
        return self.object.get_profile_url()


class UpdateAvatar(core.views.ActionMixin, django.views.generic.UpdateView):
    action = 'Avatar ändern'
    fields = ('avatar',)
    layout = ('avatar',)
    menu = 'gestalt'
    model = models.Gestalt
    permission_required = 'entities.change_gestalt'

    def get_parent(self):
        return self.object

    def get_success_url(self):
        return self.object.get_profile_url()


class UpdateBackground(core.views.ActionMixin, django.views.generic.UpdateView):
    action = 'Hintergrundbild ändern'
    fields = ('background',)
    layout = ('background',)
    menu = 'gestalt'
    model = models.Gestalt
    permission_required = 'entities.change_gestalt'

    def get_parent(self):
        return self.object

    def get_success_url(self):
        return self.object.get_profile_url()
