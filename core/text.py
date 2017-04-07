import codecs
import translitcodec   # noqa: F401, used indirectly via "translit/"

import django.utils.text


def slugify(value):
    return django.utils.text.slugify(codecs.encode(value, 'translit/long'))
