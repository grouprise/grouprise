from rest_framework import viewsets, serializers, permissions
from rest_framework.decorators import permission_classes
from sorl.thumbnail import get_thumbnail
import django_filters
import django_filters.widgets

from . import models
# todo howto resolve module without including tags here
from features.tags.rest_api import FlattenedTagSerializer
from core import api


class GroupFilter(django_filters.rest_framework.FilterSet):
    id = django_filters.Filter(name='id', lookup_expr='in',
                               widget=django_filters.widgets.CSVWidget)
    name = django_filters.CharFilter(name='name', lookup_expr='icontains')
    slug = django_filters.CharFilter(name='slug', lookup_expr='iexact')

    class Meta:
        model = models.Group
        fields = ('id', 'name', 'slug', )


class GroupSerializer(serializers.ModelSerializer):
    tags = FlattenedTagSerializer(many=True)
    initials = serializers.CharField(source='get_initials', read_only=True)
    cover = serializers.SerializerMethodField()

    def get_cover(self, instance: models.Group):
        return instance.get_cover_url()

    class Meta:
        model = models.Group
        fields = ('id', 'slug', 'name', 'initials', 'description', 'avatar',
                  'avatar_color', 'tags', 'cover', )


@permission_classes((permissions.AllowAny, ))
class GroupSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GroupSerializer
    filter_fields = ('id', 'name', 'slug', )
    filter_class = GroupFilter
    queryset = models.Group.objects.all()


@api.register
def load(router):
    router.register(r'groups', GroupSet, 'group')
