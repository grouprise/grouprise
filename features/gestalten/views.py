import allauth
import django
from allauth.account import views
from allauth.account import views as allauth_views
from crispy_forms import layout
from django.urls import reverse
from django.views import generic
from django.views.generic import edit as edit_views, DeleteView, UpdateView

import core
from core import views as utils_views
from core.views import base, PermissionMixin
from features.associations import models as associations
from features.groups.models import Group
from . import forms, models


class Create(utils_views.ActionMixin, views.SignupView):
    action = 'Registrieren'
    form_class = forms.Create
    ignore_base_templates = True
    # parent = 'gestalt-index'
    permission_required = 'account.signup'

    def get_context_data(self, **kwargs):
        kwargs['login_url'] = allauth.account.utils.passthrough_next_redirect_url(
                self.request, django.urls.reverse('account_login'),
                self.redirect_field_name)
        return django.views.generic.FormView.get_context_data(self, **kwargs)

    def get_success_url(self):
        return views.LoginView.get_success_url(self)


class Delete(PermissionMixin, DeleteView):
    permission_required = 'gestalten.delete'
    template_name = 'gestalten/delete.html'
    success_url = '/'

    def get_object(self):
        gestalt = self.request.user.gestalt
        self.data = gestalt.get_data()
        return gestalt


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


class Update(PermissionMixin, UpdateView):
    permission_required = 'gestalten.change'
    form_class = forms.Update
    template_name = 'gestalten/update.html'

    def get_context_data(self, **kwargs):
        group = Group.objects.filter(slug=self.request.GET.get('group')).first()
        if group:
            kwargs['group'] = group
        return super().get_context_data(**kwargs)

    def get_initial(self):
        return {
                'first_name': self.object.user.first_name,
                'last_name': self.object.user.last_name,
                'slug': self.object.slug,
                }

    def get_object(self):
        if self.request.user.is_authenticated:
            return self.request.user.gestalt
        else:
            return None

    def get_success_url(self):
        return self.object.get_profile_url()


class UpdateEmail(PermissionMixin, views.EmailView):
    permission_required = 'gestalten.change_email'
    form_class = forms.UpdateEmail
    template_name = 'gestalten/update_email.html'

    def get_context_data(self, **kwargs):
        group = Group.objects.filter(slug=self.request.GET.get('group')).first()
        if group:
            kwargs['group'] = group
        return super().get_context_data(**kwargs)

    @property
    def success_url(self):
        group = Group.objects.filter(slug=self.request.GET.get('group')).first()
        slug = group.slug if group else ''
        return '{}?group={}'.format(reverse('email-settings'), slug)


class UpdateEmailConfirm(utils_views.ActionMixin, edit_views.FormMixin, views.ConfirmEmailView):
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


class UpdateImages(PermissionMixin, UpdateView):
    permission_required = 'gestalten.change'
    model = models.Gestalt
    fields = ('avatar', 'background')
    template_name = 'gestalten/update_images.html'

    def get_context_data(self, **kwargs):
        group = Group.objects.filter(slug=self.request.GET.get('group')).first()
        if group:
            kwargs['group'] = group
        return super().get_context_data(**kwargs)

    def get_object(self):
        return self.request.user.gestalt


class UpdatePassword(PermissionMixin, allauth_views.PasswordChangeView):
    permission_required = 'gestalten.change_password'
    form_class = forms.UpdatePassword
    template_name = 'gestalten/update_password.html'

    def get_context_data(self, **kwargs):
        group = Group.objects.filter(slug=self.request.GET.get('group')).first()
        if group:
            kwargs['group'] = group
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return self.request.user.gestalt.get_profile_url()


class UpdatePasswordKey(utils_views.ActionMixin, views.PasswordResetFromKeyView):
    action = 'Kennwort ändern'
    form_class = forms.UpdatePasswordKey
    permission_required = 'account.reset_password'


class UpdatePasswordSet(utils_views.ActionMixin, views.PasswordSetView):
    action = 'Kennwort setzen'
    form_class = forms.UpdatePasswordSet
    ignore_base_templates = True
    permission_required = 'account.set_password'
