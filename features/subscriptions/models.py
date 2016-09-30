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
    unsubscribe = models.BooleanField(default=False)

    objects = models.Manager.from_queryset(querysets.Subscription)()

    class Meta:
        unique_together = ('content_type', 'object_id', 'subscriber')

    def update_gestalten(self, gestalten, association):
        """
        Given a list of gestalten add or remove the subscriber from this list
        if the filters of this subscription match the association
        """
        for f in self.filters:
            if not f.match(association):
                return
        if self.unsubscribe:
            gestalten.discard(self.subscriber)
        else:
            gestalten.add(self.subscriber)
