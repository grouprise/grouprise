from django_filters import ChoiceFilter, FilterSet, OrderingFilter

from grouprise.features.associations.models import Association


class ContentFilterSet(FilterSet):
    class Meta:
        model = Association
        fields = {
            'content__title': ['icontains'],
        }

    content = ChoiceFilter(
        choices=(
            ('events', 'Kommende Veranstaltungen'),
        ),
        empty_label='Alle Beiträge',
        method='content_filter',
    )

    o = OrderingFilter(
        fields=(
            ('content__time', 'Veranstaltungsdatum'),
        ),
        empty_label='Veröffentlichungsdatum (absteigend)',
    )

    def content_filter(self, queryset, name, value):
        if value == 'events':
            queryset = queryset.filter_events().filter_upcoming()
        return queryset
