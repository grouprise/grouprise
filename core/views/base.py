from django.contrib.auth import views as auth
from django.core import exceptions
from django.views import generic as django
from django.views.generic import base as django_base
from rules.contrib import views as rules


class PermissionMixin(rules.PermissionRequiredMixin):
    def get_permission_required(self):
        return (self.permission,)

    def handle_no_permission(self):
        if self.request.user.is_authenticated():
            raise exceptions.PermissionDenied(
                    self.get_permission_denied_message())
        else:
            return auth.redirect_to_login(
                    self.request.get_full_path(),
                    self.get_login_url(),
                    self.get_redirect_field_name())


class TitleMixin(django_base.ContextMixin):
    def get_context_data(self, **kwargs):
        kwargs['title'] = self.get_title()
        return super().get_context_data(**kwargs)

    def get_title(self):
        return getattr(self, 'title', None)


class View(PermissionMixin, TitleMixin, django.View):
    def get_breadcrumb_object(self):
        return self.get_title()
