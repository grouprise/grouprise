from django.db import models
import django_filters
from rest_framework import serializers


class HasLocationFilter(django_filters.BooleanFilter):
    def __init__(self, model_cls, *args, **kwargs):
        self.model_cls = model_cls
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        from .models import Location

        if value is None:
            return qs

        entity_has_location = models.Exists(
            Location.objects
            .for_locatable_type(self.model_cls)
            .filter(locatable_id=models.OuterRef("pk"))
        )
        return qs.annotate(has_location=entity_has_location).filter(has_location=value)


class LocationField(serializers.Field):
    def get_attribute(self, instance):
        return instance

    def to_representation(self, instance):
        from .models import Location

        try:
            location = Location.objects.for_locatable(instance)
        except Location.DoesNotExist:
            pass
        else:
            return {"point": str(location.point)}
        return None

    def to_internal_value(self, data):
        raise NotImplementedError()
