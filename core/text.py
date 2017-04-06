import codecs
from django.core import exceptions
from django.utils import text
import translitcodec   # noqa: F401, used indirectly via "translit/"


def slugify(value):
    return text.slugify(codecs.encode(value, 'translit/long'))
