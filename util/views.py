from . import forms
from crispy_forms import helper, layout
from django import forms as django_forms, http
from django.core import urlresolvers
from django.utils import six
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
        if hasattr(self, 'object'):
            if isinstance(self.object, entities_models.Group):
                return self.object
            if hasattr(self.object, 'group'):
                return self.object.group
            # object.groups.first()
        return None

class FormMixin(forms.LayoutMixin):
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not hasattr(form, 'helper'):
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
        if hasattr(self, 'menu'):
            kwargs['menu'] = self.menu
        return super().get_context_data(**kwargs)

class NavigationMixin:
    def get_back_url(self):
        if hasattr(self, 'back_url'):
            try:
                return urlresolvers.reverse(self.back_url)
            except urlresolvers.NoReverseMatch:
                return self.back_url
        else:
            return self.get_success_url()

    def get_context_data(self, **kwargs):
        kwargs['back_url'] = self.get_back_url()
        return super().get_context_data(**kwargs)

    def get_parent(self):
        if hasattr(self, 'parent'):
            return self.parent
        else:
            return None

    def get_success_url(self):
        parent = self.get_parent()
        if parent:
            if isinstance(parent, six.string_types):
                try:
                    return urlresolvers.reverse(parent)
                except urlresolvers.NoReverseMatch:
                    return parent
            else:
                return parent.get_absolute_url()
        else:
            try:
                return super().get_success_url()
            except AttributeError:
                return None

class PermissionMixin(rules_views.PermissionRequiredMixin):
    def get_permission_required(self):
        return (self.permission,)

class SidebarMixin:
    def get_context_data(self, **kwargs):
        kwargs['sidebar_template'] = self.sidebar_template
        return super().get_context_data(**kwargs)

class TemplateMixin:
    ignore_base_templates = False

    def get_template_names(self):
        if not self.ignore_base_templates:
            names = super().get_template_names()
        else:
            names = []
        names += ['stadt/form.html']
        return names

class TitleMixin:
    def get_context_data(self, **kwargs):
        kwargs['title'] = self.get_title()
        print(kwargs['title'])
        return super().get_context_data(**kwargs)

    def get_title(self):
        if hasattr(self, 'title'):
            return self.title
        elif hasattr(self, 'action'):
            return self.action
        else:
            return None

class ActionMixin(
        FormMixin,
        GestaltMixin,
        GroupMixin,
        MenuMixin,
        NavigationMixin,
        PermissionMixin,
        TemplateMixin,
        TitleMixin,
        ): pass

class PageMixin(
        GestaltMixin,
        MenuMixin,
        NavigationMixin,
        PermissionMixin,
        TitleMixin,
        ): pass
