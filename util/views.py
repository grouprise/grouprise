from crispy_forms import helper, layout
from entities import models as entities_models


class GroupMixin:
    def get_group(self):
        slug = self.request.resolver_match.kwargs.get('group_slug')
        return entities_models.Group.objects.get(slug=slug)


class LayoutMixin:
    def get_form(self):
        form = super().get_form()
        form.helper = helper.FormHelper()
        form.helper.layout = layout.Layout(*self.get_layout())
        return form

    def get_layout(self):
        return self.layout


class NavigationMixin:
    def get_back_url(self):
        try:
            return self.back_url
        except AttributeError:
            return self.get_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = self.get_back_url()
        return context
