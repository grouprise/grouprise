import django_filters

from grouprise.features.groups.models import Group
from grouprise.features.images.models import Image


class GroupFilter(django_filters.rest_framework.FilterSet):
    id = django_filters.Filter(
        lookup_expr="in", widget=django_filters.widgets.CSVWidget
    )
    name = django_filters.CharFilter(lookup_expr="icontains")
    slug = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = Group
        fields = (
            "id",
            "name",
            "slug",
        )


class ImageFilter(django_filters.rest_framework.FilterSet):
    id = django_filters.Filter(
        lookup_expr="in", widget=django_filters.widgets.CSVWidget
    )

    class Meta:
        model = Image
        fields = ("id", "creator")
