from rest_framework import viewsets, serializers
from features.rest_api import api
from . import models


class GestaltSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='__str__', read_only=True)
    initials = serializers.CharField(source='get_initials', read_only=True)

    class Meta:
        model = models.Gestalt
        fields = ('id', 'name', 'initials', 'about', 'avatar', 'avatar_color')


class GestaltSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GestaltSerializer
    queryset = models.Gestalt.objects.all()

    def get_queryset(self):
        user = self.request.user
        return models.Gestalt.objects.filter(pk=user.gestalt.pk)


@api.register
def load(router):
    router.register(r'gestalten', GestaltSet, 'gestalt')
