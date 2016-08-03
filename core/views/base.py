from django.contrib.auth import views as auth
from django.core import exceptions
from django.views import generic as django
from rules.contrib import views as rules


class PermissionMixin(rules.PermissionRequiredMixin):
    def get_permission_required(self):
        return self.permission

    def handle_no_permission(self):
        if self.request.user.is_authenticated():
            raise exceptions.PermissionDenied(
                    self.get_permission_denied_message())
        else:
            return auth.redirect_to_login(
                    self.request.get_full_path(),
                    self.get_login_url(),
                    self.get_redirect_field_name())


class View(PermissionMixin, django.View):
    pass
