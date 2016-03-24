from . import forms
from crispy_forms import helper, layout
from django import forms as django_forms, http
from django.views import generic
from django.views.generic import edit as edit_views
from entities import models as entities_models
from rules.contrib import views as rules_views

class DeleteView(edit_views.FormMixin, generic.DeleteView):
    pass

class GestaltMixin:
    def get_gestalt(self):
        return self.request.user.gestalt if self.request.user.is_authenticated() else None

class GroupMixin:
    def get_context_data(self, **kwargs):
        kwargs['group'] = self.get_group()
        return super().get_context_data(**kwargs)

    def get_group(self):
        if 'group_pk' in self.kwargs:
            return entities_models.Group.objects.get(pk=self.kwargs['group_pk'])
        # group_slug
        if isinstance(self.object, entities_models.Group):
            return self.object
        if hasattr(self.object, 'group'):
            return self.object.group
        # object.groups.first()
        return None

class FormMixin(forms.LayoutMixin):
    def get_form(self):
        form = super().get_form()
        form.helper = self.get_helper()
        return form

    def get_form_class(self):
        return super().get_form_class() or django_forms.Form

    def get_layout(self):
        layout = super().get_layout()
        layout += (forms.Submit(self.action),)
        return layout

class MenuMixin:
    def get_context_data(self, **kwargs):
        kwargs['menu'] = self.menu
        return super().get_context_data(**kwargs)

class NavigationMixin:
    def get_back_url(self):
        try:
            return self.back_url
        except AttributeError:
            return self.get_success_url()

    def get_context_data(self, **kwargs):
        kwargs['back_url'] = self.get_back_url()
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        parent = self.get_parent()
        if parent:
            return parent.get_absolute_url()
        else:
            return super().get_success_url()

class PermissionMixin(rules_views.PermissionRequiredMixin):
    def get_permission_required(self):
        return (self.permission,)

class SidebarMixin:
    def get_context_data(self, **kwargs):
        kwargs['sidebar_template'] = self.sidebar_template
        return super().get_context_data(**kwargs)

class TemplateMixin:
    def get_template_names(self):
        names = super().get_template_names()
        names += ['stadt/form.html']
        return names

class TitleMixin:
    def get_context_data(self, **kwargs):
        kwargs['title'] = self.action
        return super().get_context_data(**kwargs)

class ActionMixin(
        FormMixin,
        GestaltMixin,
        GroupMixin,
        MenuMixin,
        NavigationMixin,
        PermissionMixin,
        TemplateMixin,
        TitleMixin,
        ):
    pass
