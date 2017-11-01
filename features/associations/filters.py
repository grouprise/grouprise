from django_filters import ChoiceFilter, FilterSet

from . import models


class ContentFilterSet(FilterSet):
    class Meta:
        model = models.Association
        fields = []

    content = ChoiceFilter(
            choices=(
                ('all', 'Alle Beiträge (sortiert nach Veröffentlichungsdatum)'),
                ('events', 'Kommende Veranstaltungen (sortiert nach Veranstaltungsdatum)'),
            ),
            empty_label=None,
            method='content_filter')

    def content_filter(self, queryset, name, value):
        if value == 'events':
            queryset = queryset.filter_events().filter_upcoming().order_by('content__time')
        return queryset
