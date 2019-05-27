from django.forms.widgets import CheckboxInput
from django_filters import BooleanFilter

from grouprise.features.content.filters import ContentFilterSet


class TagContentFilterSet(ContentFilterSet):
    tagged_only = BooleanFilter(
            label='nur verschlagwortete Beiträge', widget=CheckboxInput,
            method='filter_tagged_only')

    def __init__(self, *args, tag=None, **kwargs):
        self.tag = tag
        super().__init__(*args, **kwargs)

    def filter_tagged_only(self, queryset, name, value):
        if value:
            queryset = queryset.filter(content__taggeds__tag=self.tag)
        return queryset
