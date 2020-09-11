import django_filters as filters
from django import forms

from grouprise.features.groups import models


class Group(filters.FilterSet):
    name = filters.CharFilter(
            label='Name', lookup_expr='icontains',
            widget=forms.TextInput(attrs={'placeholder': 'z.B. Foodcoop'}))

    only_with_membership = filters.BooleanFilter(method='filter_by_membership')

    class Meta:
        model = models.Group
        fields = ['name']

    def filter_by_membership(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            queryset = queryset.filter(members=self.request.user.gestalt)
        return queryset
