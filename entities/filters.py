from . import forms, models
import django_filters as filters


class Group(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = models.Group
        form = forms.GroupFilter
