from django.db import models
from django.contrib.gis.db.models import PointField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class LocationQuerySet(models.QuerySet):
    def for_locatable_type(self, cls):
        return self.filter(locatable_type=ContentType.objects.get_for_model(cls))


class LocationManager(models.Manager):
    def get_queryset(self):
        return LocationQuerySet(self.model, using=self._db)

    def for_locatable(self, locatable):
        return (
            self.get_queryset()
            .for_locatable_type(type(locatable))
            .get(locatable_id=locatable.pk)
        )

    def for_locatable_type(self, cls):
        return self.get_queryset().for_locatable_type(cls)


class Location(models.Model):
    objects = LocationManager()

    locatable_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    locatable_id = models.PositiveIntegerField()
    locatable = GenericForeignKey("locatable_type", "locatable_id")
    point = PointField(geography=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="locatable_location", fields=["locatable_type", "locatable_id"]
            )
        ]
