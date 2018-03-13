import django.views.generic.edit

from . import models


class ContributionFormMixin(django.views.generic.edit.FormMixin):
    def can_post(self):
        return self.request.user.has_perms((self.permission_required_post,), self.object)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_form(self):
        if self.can_post():
            return super().get_form()
        return None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['contributions'] = self.object.container.contributions
        kwargs['instance'] = models.Contribution(
                author=self.request.user.gestalt, container=self.object.container)
        return kwargs

    def has_permission(self):
        self.object = self.get_object()
        if self.request.method == 'GET':
            return super().has_permission()
        elif self.request.method == 'POST':
            return self.can_post()
        else:
            return False

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()
