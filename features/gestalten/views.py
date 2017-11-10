import allauth
import django
from django.views import generic

import core
import utils
from core.views import base
from features.associations import models as associations
from . import forms, models


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


class List(base.PermissionMixin, generic.ListView):
    permission_required = 'gestalten.view_list'
    queryset = models.Gestalt.objects.filter(public=True)
    ordering = '-score'
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


class Update(utils.views.ActionMixin, django.views.generic.UpdateView):
    action = 'Dein Profil'
    form_class = forms.Gestalt
    menu = 'gestalt'
    message = 'Die Einstellungen wurden geändert.'
    model = models.Gestalt
    permission_required = 'entities.change_gestalt'

    def get_parent(self):
        return self.object

    def get_success_url(self):
        return self.object.get_profile_url()


class UpdateAvatar(utils.views.ActionMixin, django.views.generic.UpdateView):
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


class UpdateBackground(utils.views.ActionMixin, django.views.generic.UpdateView):
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
