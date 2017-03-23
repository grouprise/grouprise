import django.views.generic.edit

from . import models


class ContributionFormMixin(django.views.generic.edit.FormMixin):

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = models.Contribution(
                author=self.request.user.gestalt, container=self.object.container)
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
