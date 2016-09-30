from . import querysets
from django.contrib.contenttypes import (
        fields as contenttypes_fields,
        models as contenttypes_models)
from django.db import models


class Subscription(models.Model):
    content_type = models.ForeignKey(contenttypes_models.ContentType)
    object_id = models.PositiveIntegerField()
    subscribed_to = contenttypes_fields.GenericForeignKey()
    subscriber = models.ForeignKey('entities.Gestalt')

    objects = models.Manager.from_queryset(querysets.Subscription)()

    class Meta:
        unique_together = ('content_type', 'object_id', 'subscriber')

    def update_gestalten(self, gestalten, association):
        for f in self.filters:
            if not f.apply(association):
                return gestalten
        if self.unsubscribe:
            gestalten.discard(self.subscriber)
        else:
            gestalten.add(self.subscriber)
        return gestalten
