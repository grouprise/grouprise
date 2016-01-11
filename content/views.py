from crispy_forms import bootstrap, helper, layout
from django.views import generic
from rules.contrib import views as rules_views

from . import models


class ContentDetail(generic.DetailView):
    model = models.Content


class ContentList(generic.ListView):
    model = models.Content


class ContentUpdate(rules_views.PermissionRequiredMixin, generic.UpdateView):
    fields = ['text', 'title']
    model = models.Content
    permission_required = 'content.change_content'

    def get_form(self):
        form = super().get_form()
        form.helper = helper.FormHelper()
        form.helper.layout = layout.Layout(
                'title',
                'text',
                bootstrap.FormActions(layout.Submit('submit', 'Beitrag speichern')),
                )
        return form
