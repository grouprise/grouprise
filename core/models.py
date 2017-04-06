from core import text
from django.contrib.contenttypes import models as contenttypes_models
from django.core import exceptions
from django.db import models


def no_validator(arg):
    pass


def validate_reservation(value):
    if value in ['gestalt', 'stadt']:
        raise exceptions.ValidationError(
                'Die Adresse \'%(value)s\' darf nicht verwendet werden.',
                params={'value': value}, code='reserved')


class AutoSlugField(models.SlugField):
    def __init__(self, *args, **kwargs):
        self.dodging = True
        if 'dodging' in kwargs:
            self.dodging = kwargs.pop('dodging')
        self.populate_from = kwargs.pop('populate_from')
        self.reserve = []
        if 'reserve' in kwargs:
            self.reserve = kwargs.pop('reserve')
        kwargs['validators'] = [validate_reservation]
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs['populate_from'] = self.populate_from
        kwargs['reserve'] = self.reserve
        return name, path, args, kwargs

    def pre_save(self, model_instance, add):
        if add:
            value = self.slugify(
                    type(model_instance), self.attname,
                    getattr(model_instance, self.populate_from),
                    validate_reservation, self.dodging)
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super().pre_save(model_instance, add)

    def slugify(self, model, field, value, validator=no_validator, dodging=True):
        orig_slug = slug = text.slugify(value)
        if not dodging:
            return slug
        i = 0
        while True:
            try:
                try:
                    validator(slug)
                except exceptions.ValidationError:
                    pass
                else:
                    model.objects.get(**{field: slug})
                i += 1
                slug = orig_slug + '-' + str(i)
            except model.DoesNotExist:
                return slug


class Model(models.Model):
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content_type = (
                contenttypes_models.ContentType.objects.get_for_model(self))
