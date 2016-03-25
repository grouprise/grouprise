from . import forms
from allauth.account import views
from crispy_forms import layout
from django.views.generic import edit as edit_views
from util import views as util_views

class Login(util_views.ActionMixin, views.LoginView):
    action = 'Anmelden'
    form_class = forms.LoginForm
    ignore_base_templates = True
    permission = 'account.login'

class Logout(util_views.ActionMixin, edit_views.FormMixin, views.LogoutView):
    action = 'Abmelden'
    ignore_base_templates = True
    layout = layout.HTML('<p>Möchtest Du Dich abmelden?</p>')
    permission = 'account.logout'

    def get_parent(self):
        return self.get_redirect_url()
