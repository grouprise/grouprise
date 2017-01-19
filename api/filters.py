import django_filters
import django_filters.widgets

import features.groups.models


class GroupFilter(django_filters.rest_framework.FilterSet):
    id = django_filters.Filter(name='id', lookup_expr='in', widget=django_filters.widgets.CSVWidget)
    name = django_filters.CharFilter(name='name', lookup_expr='icontains')

    class Meta:
        model = features.groups.models.Group
        fields = ['id', 'name']
