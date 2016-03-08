from crispy_forms import helper, layout
from entities import models as entities_models


class GroupMixin:
    def get_group(self):
        pk = self.request.resolver_match.kwargs.get('group_pk')
        slug = self.request.resolver_match.kwargs.get('group_slug')
        manager = entities_models.Group.objects
        try:
            return manager.get(slug=slug)
        except entities_models.Group.DoesNotExist:
            return manager.get(pk=pk)


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
        kwargs['back_url'] = self.get_back_url()
        return super().get_context_data(**kwargs)


class SidebarMixin:
    def get_context_data(self, **kwargs):
        kwargs['sidebar_template'] = self.sidebar_template
        return super().get_context_data(**kwargs)
