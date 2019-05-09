from django.db import models

from . import forms


class EntitySlugField(models.SlugField):
    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        forms.validate_entity_slug(value, model_instance)
