"""
Copyright 2016-2017 sense.lab e.V. <info@senselab.org>

This file is part of stadtgestalten.

stadtgestalten is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

stadtgestalten is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero Public License for more details.

You should have received a copy of the GNU Affero Public License
along with stadtgestalten.  If not, see <http://www.gnu.org/licenses/>.
"""

from . import filters, querysets
from django.contrib.contenttypes import (
        fields as contenttypes_fields,
        models as contenttypes_models)
from django.db import models


class Filter(models.Model):
    filter_id = models.PositiveSmallIntegerField()
    subscription = models.ForeignKey('Subscription', related_name='filters')

    def match(self, association):
        return filters.filters[self.filter_id](association)


class Subscription(models.Model):
    content_type = models.ForeignKey(contenttypes_models.ContentType)
    object_id = models.PositiveIntegerField()
    subscribed_to = contenttypes_fields.GenericForeignKey()
    subscriber = models.ForeignKey('gestalten.Gestalt', related_name='subscriptions')
    unsubscribe = models.BooleanField(default=False)

    objects = querysets.SubscriptionManager.from_queryset(querysets.Subscription)()

    class Meta:
        unique_together = ('content_type', 'object_id', 'subscriber')

    def update_gestalten(self, gestalten, association):
        """
        Given a set of gestalten add or remove the subscriber from this set
        if the filters of this subscription match the association
        """
        filters = self.filters.all()
        # only try updating on new-style subscriptions with at least one filter
        if filters:
            # exit if one of the filters doesn't match
            for f in filters:
                if not f.match(association):
                    return
            # update based on unsubscribe flag
            if self.unsubscribe:
                gestalten.discard(self.subscriber)
            else:
                gestalten.add(self.subscriber)


class Unsubscription(Subscription):
    objects = querysets.UnsubscriptionManager.from_queryset(querysets.Subscription)()

    class Meta:
        proxy = True


class SubOrUnsubscription(Subscription):
    objects = models.Manager.from_queryset(querysets.Subscription)()

    class Meta:
        proxy = True
