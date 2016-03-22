from crispy_forms import bootstrap, helper, layout
from django import http
from entities import models as entities_models

class GestaltMixin:
    def get_gestalt(self):
        return self.request.user.gestalt if self.request.user.is_authenticated() else None

def get_group_by_kwarg(request, **kwargs):
    group = None
    for field, arg_key in kwargs.items():
        try:
            kwarg = request.resolver_match.kwargs.get(arg_key)
            group = entities_models.Group.objects.get(**{field: kwarg})
            break
        except entities_models.Group.DoesNotExist:
            continue
    if not group and kwarg:
        raise http.Http404('Group not found by argument {}.'.format(kwarg))
    return group

class GroupMixin:
    def get_group(self):
        group = get_group_by_kwarg(self.request, pk='group_pk', slug='group_slug')
        if not group:
            try:
                group = self.object.groups.first()
            except AttributeError:
                pass
        return group

def submit(text):
    return bootstrap.FormActions(layout.Submit('submit', text))

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
