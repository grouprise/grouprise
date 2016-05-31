import codecs
from django.utils import text
import translitcodec

def slugify(model, field, value):
    orig_slug = slug = text.slugify(codecs.encode(value, 'translit/long'))[:45]
    i = 0
    while True:
        try:
            model.objects.get(**{field: slug})
            i += 1
            slug = orig_slug + '-' + str(i)
        except model.DoesNotExist:
            return slug
