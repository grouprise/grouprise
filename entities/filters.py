from . import forms
import django_filters as filters
from features.groups import models


class Group(filters.FilterSet):
    name = filters.CharFilter(label='Name', lookup_expr='icontains')

    class Meta:
        model = models.Group
        fields = ['name']
        form = forms.GroupFilter
