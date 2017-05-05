"""
Copyright 2016-2017 sense.lab e.V. <info@senselab.org>

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

    class Meta:
        model = models.Group
        fields = ('id', 'name')


class GroupSerializer(serializers.ModelSerializer):
    tags = FlattenedTagSerializer(many=True)
    initials = serializers.CharField(source='get_initials', read_only=True)

    def to_representation(self, instance: models.Group):
        repr = super().to_representation(instance)
        gallery = instance.get_head_gallery()
        if gallery and gallery.images.first():
            image = gallery.images.first().file
            repr['cover'] = get_thumbnail(image, '360x120', crop='center').url
        else:
            repr['cover'] = None
        return repr

    class Meta:
        model = models.Group
        fields = ('id', 'name', 'initials', 'description', 'avatar', 'avatar_color', 'tags')


@permission_classes((permissions.AllowAny, ))
class GroupSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GroupSerializer
    filter_fields = ('id', 'name', )
    filter_class = GroupFilter
    queryset = models.Group.objects.all()


@api.register
def load(router):
    router.register(r'groups', GroupSet, 'group')
