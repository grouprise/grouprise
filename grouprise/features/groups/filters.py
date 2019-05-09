import django_filters as filters
from django import forms

from grouprise.features.groups import models


class Group(filters.FilterSet):
    name = filters.CharFilter(
            label='Name', lookup_expr='icontains',
            widget=forms.TextInput(attrs={'placeholder': 'z.B. Foodcoop'}))

    class Meta:
        model = models.Group
        fields = ['name']
