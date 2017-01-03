"""
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

from django.contrib.contenttypes import models as contenttypes_models
from django.db import models


class Subscription(models.QuerySet):
    def filter(self, **kwargs):
        if 'subscribed_to' in kwargs:
            instance = kwargs.pop('subscribed_to')
            content_type = contenttypes_models.ContentType.objects \
                .get_for_model(instance)
            return super().filter(
                    content_type=content_type,
                    object_id=instance.id,
                    **kwargs)
        return super().filter(**kwargs)


class SubscriptionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(unsubscribe=False)


class UnsubscriptionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(unsubscribe=True)
