from rest_framework import permissions


class RulesPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        return view.has_permission()
