import codecs
from django.core import exceptions
from django.utils import text
import translitcodec   # noqa: F401, used indirectly via "translit/"


def no_validator(arg):
    pass


def slugify(model, field, value, validator=no_validator):
    orig_slug = slug = text.slugify(codecs.encode(value, 'translit/long'))[:45]
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
