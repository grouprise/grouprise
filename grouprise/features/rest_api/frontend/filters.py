import django_filters

from grouprise.features.images.models import Image


class ImageFilter(django_filters.rest_framework.FilterSet):
    id = django_filters.Filter(lookup_expr='in', widget=django_filters.widgets.CSVWidget)

    class Meta:
        model = Image
        fields = ('id', 'creator')
