from . import models
from crispy_forms import bootstrap, helper, layout
from django.core import urlresolvers
from django.views import generic
from entities import models as entities_models
from rules.contrib import views as rules_views


class ContentDetail(generic.DetailView):
    model = models.Content


class ContentList(generic.ListView):
    model = models.Content


class ContentUpdate(rules_views.PermissionRequiredMixin, generic.UpdateView):
    fields = ['text', 'title']
    layout = [
            'title',
            'text',
            bootstrap.FormActions(layout.Submit('submit', 'Beitrag speichern')),
            ]
    model = models.Content
    permission_required = 'content.change_content'

    def get_form(self):
        form = super().get_form()
        form.helper = helper.FormHelper()
        form.helper.layout = layout.Layout(*self.layout)
        return form

    def get_group(self):
        slug = self.request.resolver_match.kwargs.get('group_slug')
        return entities_models.Group.objects.get(slug=slug)

    def get_success_url(self):
        try:
            return urlresolvers.reverse('group-content', args=[self.get_group().slug, self.get_object().slug])
        except entities_models.Group.DoesNotExist:
            return super().get_success_url()
