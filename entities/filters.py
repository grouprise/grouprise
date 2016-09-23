from . import forms, models
import django_filters as filters
from features.groups import models as groups


class Group(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = groups.Group
        form = forms.GroupFilter
