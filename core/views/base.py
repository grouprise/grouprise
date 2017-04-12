from django.contrib.auth import views as auth
from django.core import exceptions, urlresolvers
from django.utils import six
from django.views import generic as django
from django.views.generic import base as django_base
from rest_framework.authentication import BasicAuthentication

from rules.contrib import views as rules


class PermissionMixin(rules.PermissionRequiredMixin):
    """
    Handle permissions
    """
    def get_permission_required(self):
        if not hasattr(self, 'permission'):
            return super().get_permission_required()
        else:
            return (self.permission,)

    def handle_no_permission(self):
        if self.request.user.is_authenticated():
            raise exceptions.PermissionDenied(
                    self.get_permission_denied_message())
        else:
            return auth.redirect_to_login(
                    self.request.get_full_path(),
                    self.get_login_url(),
                    self.get_redirect_field_name())


class StadtMixin(django_base.ContextMixin):
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
                url = urlresolvers.reverse(instance)
                title = urlresolvers.resolve(url).func.view_class.title
            else:
                url = instance.get_absolute_url()
        except (AttributeError, urlresolvers.NoReverseMatch):
            url = None
        return title, url

    def get_grandparent(self, parent):
        return None

    def get_parent(self):
        return getattr(self, 'parent', None)

    def get_title(self):
        return getattr(self, 'title', None)


class View(PermissionMixin, StadtMixin, django.View):
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


class HTTPAuthMixin:

    def get_http_auth_gestalt(self):
        """ retrieve a gestalt that was authenticated via HTTP authentication

        Fail silently and return None if not authentication happened. An HTTP authentication can
        be forced later by responding with a 401 HTTP status code. This relaxed approach allows to
        combine this authentication method with other fallback methods.
        """
        auth = BasicAuthentication()
        try:
            result = auth.authenticate(self.request)
        except (exceptions.NotAuthenticated, exceptions.AuthenticationFailed) as exc:
            return None
        if result is None:
            return None
        else:
            return result[0].gestalt


class GestaltAuthenticationMixin(HTTPAuthMixin):

    def get_authenticated_gestalt(self, target):
        """ retrieve a gestalt that is authenticated via HTTP-Auth or via a permission token

        No authorization checks ("is the gestalt allowed to do something") is performed.
        """
        return self.get_http_auth_gestalt()
