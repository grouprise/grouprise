import codecs
import translitcodec   # noqa: F401, used indirectly via "translit/"

import django.utils.text


def intify(string, default=0):
    if string is None:
        return default
    else:
        try:
            return int(string)
        except ValueError:
            return default


def slugify(value):
    return django.utils.text.slugify(codecs.encode(value, 'translit/long'))
