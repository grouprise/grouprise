from django_filters import ChoiceFilter, FilterSet


class Event(FilterSet):
    content = ChoiceFilter(
            choices=(
                ('all', 'Standard (alle Beiträge)'),
                ('events', 'Veranstaltungen (zukünftige)'),
            ),
            method='content_filter')

    def content_filter(self, queryset, name, value):
        if value == 'events':
            queryset = queryset.filter_events()
        return queryset
