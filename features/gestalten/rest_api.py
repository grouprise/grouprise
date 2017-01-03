"""
This file is part of stadtgestalten.

stadtgestalten is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

stadtgestalten is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero Public License for more details.

You should have received a copy of the GNU Affero Public License
along with stadtgestalten.  If not, see <http://www.gnu.org/licenses/>.
"""

from rest_framework import viewsets, serializers, permissions
from core import api
from . import models


def permission(path):
    class UserPermission(permissions.BasePermission):
        def has_permission(self, request, view):
            gestalt_id = request.resolver_match.kwargs.get('gestalt')
            return request.user.gestalt.id == int(gestalt_id)

        def has_object_permission(self, request, view, obj):
            return request.user.gestalt == path(obj)
    return UserPermission


class GestaltSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='__str__', read_only=True)
    initials = serializers.CharField(source='get_initials', read_only=True)

    class Meta:
        model = models.Gestalt
        fields = ('id', 'name', 'initials', 'about', 'avatar', 'avatar_color')


class GestaltSettingSerializer(serializers.ModelSerializer):
    def get_fields(self):
        fields = super().get_fields()
        gestalt = self.context['view'].request.user.gestalt
        fields['gestalt'].queryset = models.Gestalt.objects.filter(id=gestalt.id)
        return fields

    class Meta:
        model = models.GestaltSetting
        fields = ('id', 'gestalt', 'name', 'category', 'value')


class GestaltSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GestaltSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        user = self.request.user
        return models.Gestalt.objects.filter(pk=user.gestalt.pk)


class GestaltSettingSet(viewsets.ModelViewSet):
    serializer_class = GestaltSettingSerializer
    permission_classes = (permissions.IsAuthenticated, permission(lambda setting: setting.gestalt))

    def get_queryset(self):
        return models.GestaltSetting.objects.filter(gestalt=self.kwargs['gestalt'])


@api.register
def load(router):
    router.register(r'gestalten', GestaltSet, 'gestalt')
    router.register(r'gestalten/(?P<gestalt>\d+)/settings', GestaltSettingSet, 'gestalt_setting')
