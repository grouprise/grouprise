from rest_framework import viewsets, serializers, permissions
from rest_framework.decorators import permission_classes
import django_filters.widgets

from grouprise.features.groups import models
from grouprise.features.tags.rest_api import TagSerializer


class GroupFilter(django_filters.rest_framework.FilterSet):
    id = django_filters.Filter(lookup_expr='in', widget=django_filters.widgets.CSVWidget)
    name = django_filters.CharFilter(lookup_expr='icontains')
    slug = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = models.Group
        fields = ('id', 'name', 'slug', )


class GroupSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    initials = serializers.CharField(source='get_initials', read_only=True)
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    cover = serializers.SerializerMethodField()

    def get_cover(self, obj: models.Group):
        return obj.get_cover_url()

    class Meta:
        model = models.Group
        fields = ('id', 'slug', 'name', 'initials', 'description', 'avatar',
                  'avatar_color', 'tags', 'cover', 'url', )


@permission_classes((permissions.AllowAny, ))
class GroupSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GroupSerializer
    filter_fields = ('id', 'name', 'slug', )
    filter_class = GroupFilter
    queryset = models.Group.objects.all()
