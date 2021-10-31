from calendar import different_locale
import locale

import randomcolor
import codecs
import translitcodec  # noqa: F401, used indirectly via "translit/"

import django.utils.text
from django.utils.translation import get_language, get_language_from_request, to_locale


def slugify(value):
    return django.utils.text.slugify(codecs.encode(value, "translit/long"))


def get_random_color():
    return randomcolor.RandomColor().generate(luminosity="dark")[0]


def get_verified_locale(request=None):
    """determine the wanted locale based on the requested or configured language

    The availability of the locale is verified by configuring it temporarily.
    """
    # use request language or fall back to the configured language
    if request is not None:
        lang = get_language_from_request(request)
    else:
        lang = get_language()
    if lang is not None:
        # Django uses UTF-8 encoding
        loc = locale.normalize(to_locale(lang) + ".UTF-8")
        try:
            # verify that the locale is available on the local system
            with different_locale(loc):
                return loc
        except locale.Error:
            # the configured/requested locale is unavailable
            pass
    else:
        return None
