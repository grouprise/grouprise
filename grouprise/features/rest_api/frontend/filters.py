import django_filters
from django_filters import rest_framework as filters

from grouprise.features.groups.models import Group
from grouprise.features.images.models import Image


class ContentFilterSet(filters.FilterSet):

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
    name = django_filters.CharFilter(lookup_expr='icontains')
    slug = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Group
        fields = ('id', 'name', 'slug', )


class ImageFilter(django_filters.rest_framework.FilterSet):
    id = django_filters.Filter(lookup_expr='in', widget=django_filters.widgets.CSVWidget)

    class Meta:
        model = Image
        fields = ('id', 'creator')
