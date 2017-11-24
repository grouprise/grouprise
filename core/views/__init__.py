# Obsolete code. Do not use for new views. Use django.views.generic instead.

import django
import json

from .base import PermissionMixin, View  # NOQA
from .edit import CreateView as Create, FormView as Form  # NOQA

from core import forms
from crispy_forms import layout
from django import forms as django_forms, http
from django.contrib.messages import views as messages_views
from django.core import exceptions, urlresolvers
from django.utils import six
from django.views import generic
from django.views.generic import edit as edit_views
from features.gestalten import models as entities_models
from features.groups import models as groups


class GestaltMixin:
    def get_context_data(self, **kwargs):
        kwargs['gestalt'] = self.get_gestalt()
        return super().get_context_data(**kwargs)

    def get_gestalt(self):
        try:
            if 'gestalt_pk' in self.kwargs:
                return entities_models.Gestalt.objects.get(pk=self.kwargs['gestalt_pk'])
            if 'gestalt_slug' in self.kwargs:
                return entities_models.Gestalt.objects.get(
                        user__username=self.kwargs['gestalt_slug'])
            if 'entity_slug' in self.kwargs:
                return entities_models.Gestalt.objects.get(
                        user__username=self.kwargs['entity_slug'])
        except entities_models.Gestalt.DoesNotExist:
            pass

        return None


class GroupMixin:
    def get_context_data(self, **kwargs):
        kwargs['group'] = self.get_group()
        return super().get_context_data(**kwargs)

    def get_group(self):
        for attr in ('object', 'related_object'):
            if hasattr(self, attr):
                instance = getattr(self, attr)
                if isinstance(instance, groups.Group):
                    return instance
                if hasattr(instance, 'group'):
                    return instance.group
                # if hasattr(instance, 'groups'):
                #     return instance.groups.first()
        try:
            if 'group_pk' in self.kwargs:
                return groups.Group.objects.get(pk=self.kwargs['group_pk'])
            if 'group_slug' in self.kwargs:
                return groups.Group.objects.get(slug=self.kwargs['group_slug'])
            if 'entity_slug' in self.kwargs:
                return groups.Group.objects.get(slug=self.kwargs['entity_slug'])
            if 'group' in self.request.GET:
                return groups.Group.objects.get(slug=self.request.GET['group'])
        except groups.Group.DoesNotExist:
            pass
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
        if hasattr(self, '_fields'):
            lay = self._fields
        else:
            lay = super().get_layout()
        if hasattr(self, 'description'):
            lay = (layout.HTML('<p>{}</p>'.format(self.description)),) + lay
        lay += (forms.Submit(self.get_action()),)
        return lay


class InlineViewMixin:
    def get_context_data(self, **kwargs):
        if hasattr(self, 'inline_view'):
            kwargs[self.inline_view[1]] = self.get_inline_view_form()
        return super().get_context_data(**kwargs)

    def get_inline_view_form(self):
        v = self.inline_view[0]()
        v.request = self.request
        v.args = self.args
        v.kwargs = self.kwargs
        if hasattr(self, 'get_inline_view_kwargs'):
            v.kwargs.update(self.get_inline_view_kwargs())
        return v.get_form()


class MenuMixin:
    def get_context_data(self, **kwargs):
        menu = self.get_menu()
        if menu and not isinstance(menu, six.string_types):
            menu = menu.__name__
        kwargs['menu'] = menu
        return super().get_context_data(**kwargs)

    def get_menu(self):
        if hasattr(self, 'menu'):
            return self.menu
        for instance in (getattr(self, 'related_object', None), self.get_parent()):
            if instance:
                t = type(instance)
                return t
        return None


class MessageMixin(messages_views.SuccessMessageMixin):
    def get_success_message(self, cleaned_data):
        if hasattr(self, 'message'):
            return self.message
        return None


class NavigationMixin:
    def get_breadcrumb(self):
        objects = [self.get_parent(), self.get_breadcrumb_object()]
        objects = [o for o in objects if o is not None]
        if objects:
            entity = self.get_parent_entity(objects[0])
            if entity:
                objects.insert(0, entity)
            breadcrumb = [self.get_navigation_data(o) for o in objects[:-1]]
            breadcrumb.append((str(objects[-1]), None))
            return breadcrumb
        return []

    def get_context_data(self, **kwargs):
        kwargs['breadcrumb'] = self.get_breadcrumb()
        return super().get_context_data(**kwargs)

    def get_navigation_data(self, instance):
        title = str(instance)
        try:
            if isinstance(instance, six.string_types):
                url = urlresolvers.reverse(instance)
                title = urlresolvers.resolve(url).func.view_class.title
            else:
                url = instance.get_absolute_url()
        except (AttributeError, urlresolvers.NoReverseMatch):
            url = None
        return title, url

    def get_parent(self):
        if hasattr(self, 'parent'):
            return self.parent
        else:
            None

    def get_parent_entity(self, child):
        return None

    def get_success_url(self):
        try:
            return super().get_success_url()
        except (AttributeError, exceptions.ImproperlyConfigured):
            return self.get_navigation_data(self.get_parent())[1]


class PaginationMixin:
    paginate_by = 10


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


class TitleMixin:
    def get_action(self):
        if hasattr(self, 'action'):
            return self.action
        else:
            return None

    def get_breadcrumb_object(self):
        return self.get_title()

    def get_context_data(self, **kwargs):
        kwargs['title'] = self.get_title()
        return super().get_context_data(**kwargs)

    def get_title(self):
        if hasattr(self, 'title'):
            return self.title
        else:
            return self.get_action()


class ActionMixin(
        FormMixin,
        GestaltMixin,
        GroupMixin,
        InlineViewMixin,
        MenuMixin,
        MessageMixin,
        NavigationMixin,
        PermissionMixin,
        TemplateMixin,
        TitleMixin,
        ):
    fallback_template_name = 'stadt/form.html'
    sidebar = tuple()


class PageMixin(
        GestaltMixin,
        GroupMixin,
        InlineViewMixin,
        MenuMixin,
        NavigationMixin,
        PaginationMixin,
        PermissionMixin,
        TemplateMixin,
        TitleMixin,
        ):
    fallback_template_name = 'stadt/stadt.html'


class RelatedObjectMixin:
    related_object_mandatory = True

    def dispatch(self, request, *args, **kwargs):
        self.related_object = self.get_related_object()
        if self.related_object_mandatory and not self.related_object:
            raise http.Http404('Zugehöriges Objekt nicht gefunden')
        return super().dispatch(request, *args, **kwargs)


class OldCreate(RelatedObjectMixin, ActionMixin, generic.CreateView):
    def __init__(self, *args, **kwargs):
        self._fields = self.fields
        self.fields = self.get_fields()
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_field_name(field):
        if isinstance(field, layout.Field):
            return field.fields[0]
        else:
            return field

    def get_fields(self):
        return [self.get_field_name(f) for f in self._fields]

    def get_form(self):
        form = super().get_form()
        for field in self._fields:
            if getattr(field, 'constant', False):
                form.fields[self.get_field_name(field)].disabled = True
        return form

    def get_parent(self):
        return self.related_object

    def get_permission_object(self):
        return self.related_object


class Delete(RelatedObjectMixin, ActionMixin, edit_views.FormMixin, generic.DeleteView):
    def get_parent(self):
        return self.related_object


class List(RelatedObjectMixin, PageMixin, generic.ListView):
    related_object_mandatory = False

    def get_permission_object(self):
        return self.related_object

    def get_related_object(self):
        return None


class Error(django.views.generic.View):
    def dispatch(self, *args, **kwargs):
        raise RuntimeError('Intentionally raised an error!')


class AppConfig:
    def __init__(self):
        self._settings = {}
        self._defaults = {}

    def add_setting(self, name, value):
        self._settings[name] = value
        return self

    def add_default(self, name, value):
        self._defaults[name] = value
        return self

    def serialize(self):
        conf = {}
        conf.update(self._defaults)
        conf.update(self._settings)
        return json.dumps(conf)


app_config = AppConfig()
