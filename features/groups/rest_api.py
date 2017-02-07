from rest_framework import viewsets, serializers
import django_filters
import django_filters.widgets

from . import models
# todo howto resolve module without including tags here
from features.tags.rest_api import TagSerializer
from core import api


class GroupFilter(django_filters.rest_framework.FilterSet):
    id = django_filters.Filter(name='id', lookup_expr='in',
                               widget=django_filters.widgets.CSVWidget)
    name = django_filters.CharFilter(name='name', lookup_expr='icontains')

    class Meta:
        model = models.Group
        fields = ('id', 'name')


class GroupSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    initials = serializers.CharField(source='get_initials', read_only=True)

    class Meta:
        model = models.Group
        fields = ('id', 'name', 'initials', 'description', 'avatar', 'avatar_color', 'tags')


class GroupSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GroupSerializer
    filter_fields = ('id', 'name', )
    filter_class = GroupFilter
    queryset = models.Group.objects.all()


@api.register
def load(router):
    router.register(r'groups', GroupSet, 'group')
