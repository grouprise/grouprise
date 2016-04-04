from . import forms
from crispy_forms import helper, layout
from django import forms as django_forms, http
from django.contrib.messages import views as messages_views
from django.core import exceptions, urlresolvers
from django.utils import six
from django.views import generic
from django.views.generic import edit as edit_views
from entities import models as entities_models
from rules.contrib import views as rules_views

class DeleteView(edit_views.FormMixin, generic.DeleteView):
    pass

class GroupMixin:
    def get_context_data(self, **kwargs):
        kwargs['group'] = self.get_group()
        return super().get_context_data(**kwargs)

    def get_group(self):
        if hasattr(self, 'object'):
            if isinstance(self.object, entities_models.Group):
                return self.object
            if hasattr(self.object, 'group'):
                return self.object.group
            if hasattr(self.object, 'groups'):
                return self.object.groups.first()
        if 'group_pk' in self.kwargs:
            return entities_models.Group.objects.get(pk=self.kwargs['group_pk'])
        if 'group' in self.request.GET:
            return entities_models.Group.objects.get(slug=self.request.GET['group'])
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
        kwargs['menu'] = self.get_menu()
        return super().get_context_data(**kwargs)

    def get_menu(self):
        if hasattr(self, 'menu'):
            return self.menu

class MessageMixin(messages_views.SuccessMessageMixin):
    def get_success_message(self, cleaned_data):
        if hasattr(self, 'message'):
            return self.message
        else:
            return None

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
    def get_permissions(self):
        return {self.permission: self.get_permission_object()}

    def has_permission(self, permission=None):
        permissions = self.get_permissions()
        if permission in permissions:
            permissions = {permission: permissions[permission]}
        for permission, object in permissions.items():
            if self.request.user.has_perm(permission, object):
                return True
        return False

class SidebarMixin:
    sidebar = ('calendar', 'groups')

    def get_context_data(self, **kwargs):
        kwargs['sidebar'] = self.sidebar
        return super().get_context_data(**kwargs)

class TemplateMixin:
    ignore_base_templates = False

    def get_template_names(self):
        if not self.ignore_base_templates:
            try:
                names = super().get_template_names()
            except exceptions.ImproperlyConfigured:
                names = []
        else:
            names = []
        names += [self.fallback_template_name]
        return names

class ActionTemplateMixin(TemplateMixin):
    fallback_template_name = 'stadt/form.html'

class PageTemplateMixin(TemplateMixin):
    fallback_template_name = 'stadt/list.html'

class TitleMixin:
    def get_context_data(self, **kwargs):
        kwargs['title'] = self.get_title()
        return super().get_context_data(**kwargs)

    def get_title(self):
        if hasattr(self, 'title'):
            return self.title
        elif hasattr(self, 'action'):
            return self.action
        else:
            return None

class ActionMixin(
        ActionTemplateMixin,
        FormMixin,
        GroupMixin,
        MenuMixin,
        MessageMixin,
        NavigationMixin,
        PermissionMixin,
        TitleMixin,
        ): pass

class PageMixin(
        GroupMixin,
        MenuMixin,
        NavigationMixin,
        PageTemplateMixin,
        PermissionMixin,
        SidebarMixin,
        TitleMixin,
        ): pass
