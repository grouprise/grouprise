from rest_framework import permissions, viewsets
from rest_framework.response import Response

from grouprise.core.templatetags.defaulttags import markdown
from grouprise.features.gestalten.models import Gestalt, GestaltSetting
from .serializers import GestaltSerializer, GestaltSettingSerializer

_PRESETS = {
    'content': {
        'heading_baselevel': 2,
    },
}


def permission(path):
    class UserPermission(permissions.BasePermission):
        def has_permission(self, request, view):
            gestalt_id = request.resolver_match.kwargs.get('gestalt')
            return request.user.gestalt.id == int(gestalt_id)

        def has_object_permission(self, request, view, obj):
            return request.user.gestalt == path(obj)
    return UserPermission


class GestaltSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GestaltSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        user = self.request.user
        return Gestalt.objects.filter(pk=user.gestalt.pk)


class GestaltSettingSet(viewsets.ModelViewSet):
    serializer_class = GestaltSettingSerializer
    permission_classes = (permissions.IsAuthenticated, permission(lambda setting: setting.gestalt))

    def get_queryset(self):
        return GestaltSetting.objects.filter(gestalt=self.kwargs['gestalt'])


class MarkdownView(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated, )

    def create(self, request, *args, **kwargs):
        preset = _PRESETS[request.data.get('preset', 'content')]
        text = request.data.get('content')
        return Response({
            'content': str(markdown(text, **preset))
        })
