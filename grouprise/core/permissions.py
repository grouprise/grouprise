from rest_framework import permissions


class RulesPermissions(permissions.BasePermission):
    """Default permission class used with Django Rest Framework

    .. seealso:: https://www.django-rest-framework.org/api-guide/permissions/
    """

    def has_permission(self, request, view):
        try:
            return view.has_permission()
        except AttributeError:
            return False
