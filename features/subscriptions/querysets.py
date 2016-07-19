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
