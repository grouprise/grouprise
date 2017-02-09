from rest_framework import permissions
from stadt.settings import DEBUG


class RulesPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            return view.has_permission()
        except AttributeError:
            return DEBUG
