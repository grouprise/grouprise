from django.db import models
from django.contrib.gis.db.models import PointField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Location(models.Model):
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
