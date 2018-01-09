from django import urls
from django.utils import six
from django.views import generic as django_generic_views
from django.views.generic import base as django_generic_views_base

from rules.contrib import views as rules


class PermissionMixin(rules.PermissionRequiredMixin):
    @property
    def raise_exception(self):
        return self.request.user.is_authenticated()


class StadtMixin(django_generic_views_base.ContextMixin):
    """
    Insert Stadtgestalten specific attributes into context
    """
    def get_breadcrumb(self):
        objects = list(filter(None, [self.get_parent(), self.get_title()]))
        if objects:
            grandparent = self.get_grandparent(objects[0])
            if grandparent:
                objects.insert(0, grandparent)
            breadcrumb = [self.get_navigation_data(o) for o in objects[:-1]]
            breadcrumb.append((str(objects[-1]), None))
            return breadcrumb
        return []

    def get_context_data(self, **kwargs):
        kwargs['breadcrumb'] = self.get_breadcrumb()
        kwargs['menu'] = self.get_menu()
        kwargs['title'] = self.get_title()
        return super().get_context_data(**kwargs)

    def get_menu(self):
        return getattr(self, 'menu', None)

    def get_navigation_data(self, instance):
        title = str(instance)
        try:
            if isinstance(instance, six.string_types):
                url = urls.reverse(instance)
                title = urls.resolve(url).func.view_class.title
            else:
                url = instance.get_absolute_url()
        except (AttributeError, urls.NoReverseMatch):
            url = None
        return title, url

    def get_grandparent(self, parent):
        return None

    def get_parent(self):
        return getattr(self, 'parent', None)

    def get_title(self):
        return getattr(self, 'title', None)


class View(PermissionMixin, StadtMixin, django_generic_views.View):
    """
    Stadtgestalten base view
    """
    def dispatch(self, *args, **kwargs):
        self.object = getattr(self, 'object', None)
        self.related_object = self.get_view_object(None)
        return super().dispatch(*args, **kwargs)

    def get_menu(self):
        if self.related_object:
            return type(self.related_object).__name__
        else:
            return super().get_menu()

    def get_parent(self):
        return self.related_object or super().get_parent()

    def get_permission_object(self):
        return self.related_object

    def get_view_object(self, key):
        if key is None and hasattr(self, 'get_related_object'):
            return self.get_related_object()
        return None
