from rest_framework import viewsets, serializers, permissions
from rest_framework.decorators import permission_classes
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


class TransitionConnectGroupListSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    permalink = serializers.SerializerMethodField()
    timestamp = serializers.SerializerMethodField()

    def get_permalink(self, obj: models.Group):
        return self.context['request'].build_absolute_uri(obj.get_absolute_url())

    def get_timestamp(self, obj: models.Group):
        return int(obj.time_modified.timestamp())

    class Meta:
        model = models.Group
        fields = ('id', 'permalink', 'timestamp')


class TransitionConnectGroupSerializer(TransitionConnectGroupListSerializer):
    website = serializers.CharField(source='url', read_only=True)
    categories = serializers.SerializerMethodField()
    admins = serializers.SerializerMethodField()
    slogan = serializers.SerializerMethodField()
    locations = serializers.SerializerMethodField()

    def get_categories(self, obj: models.Group):
        # TODO: we don’t have categories for groups yet, only tags. should we deliver those?
        return []

    def get_admins(self, obj: models.Group):
        # TODO: should we consider members admins and if so, are we happy to provide
        #       their mail-address to the outside world?
        return []

    def get_slogan(self, obj: models.Group):
        # TODO: groups don’t have slogans
        return None

    def get_locations(self, obj: models.Group):
        # TODO: groups only have a single address, but we don’t support a description
        #       or any kind of geo-data for them
        address = ', '.join(obj.address.replace('\r', '').split('\n')) \
            if obj.address else None
        return [{
            'address': address,
            'description': None,
            'geo': None
        }]

    class Meta:
        model = models.Group
        fields = (
            'id', 'permalink', 'timestamp', 'name', 'description', 'admins',
            'categories', 'website', 'slogan', 'locations'
        )


@permission_classes((permissions.AllowAny, ))
class TransitionGroupSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Group.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return TransitionConnectGroupListSerializer
        return TransitionConnectGroupSerializer


@api.register
def load(router):
    router.register(r'groups', GroupSet, 'group')
    router.register(r'organisation', TransitionGroupSet, 'organisation')
