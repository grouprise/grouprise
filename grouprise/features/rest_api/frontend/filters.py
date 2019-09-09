from functools import reduce

import django_filters
from django.db.models import Q
from django_filters import rest_framework as filters

from grouprise.features.associations.models import Association
from grouprise.features.groups.models import Group
from grouprise.features.images.models import Image


class ContentFilterSet(filters.FilterSet):
    
    keywords = filters.CharFilter(method='filter_keywords')

    type = filters.ChoiceFilter(
        choices=(
            ('articles', 'Artikel'),
            ('events', 'Veranstaltungen'),
            ('upcoming-events', 'Kommende Veranstaltungen'),
        ),
        empty_label='Alle',
        method='filter_type',
    )

    ordering = filters.OrderingFilter(
        fields={
            'time_created': 'pub_time',
            'content__time': 'ev_time',
        },
    )

    def filter_keywords(self, queryset, name, value):
        lookups = ['content__title__icontains', 'slug__icontains']
        keywords = value.split()
        for keyword in keywords:
            q_expressions = [Q(**{l: keyword}) for l in lookups]
            queryset = queryset.filter(reduce(lambda q1, q2: q1 | q2, q_expressions))
        return queryset

    def filter_type(self, queryset, name, value):
        if value == 'articles':
            queryset = queryset.filter_articles()
        elif value == 'events':
            queryset = queryset.filter_events()
        elif value == 'upcoming-events':
            queryset = queryset.filter_events().filter_upcoming()
        return queryset


class GroupFilterSet(filters.FilterSet):
    id = django_filters.Filter(lookup_expr='in', widget=django_filters.widgets.CSVWidget)
    membership = filters.BooleanFilter(method='filter_membership')
    name = django_filters.CharFilter(lookup_expr='icontains')
    slug = django_filters.CharFilter(lookup_expr='iexact')
    subscription = filters.BooleanFilter(method='filter_subscription')

    ordering = filters.OrderingFilter(
        fields={
            'score': 'activity',
            'name': 'name',
        },
    )

    class Meta:
        model = Group
        fields = ('id', 'name', 'slug', )

    def filter_membership(self, queryset, _, value):
        if value:
            queryset = queryset.filter(members=self.request.user.gestalt)
        return queryset

    def filter_subscription(self, queryset, _, value):
        if value:
            queryset = queryset.filter(subscriptions__subscriber=self.request.user.gestalt)
        return queryset


class ImageFilter(django_filters.rest_framework.FilterSet):
    id = django_filters.Filter(lookup_expr='in', widget=django_filters.widgets.CSVWidget)

    class Meta:
        model = Image
        fields = ('id', 'creator')
