from . import forms
import django_filters as filters


class Group(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        form = forms.GroupFilter
