from django.contrib.contenttypes import models as contenttypes_models
from django.db import models


class Model(models.Model):
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content_type = (
                contenttypes_models.ContentType.objects.get_for_model(self))
