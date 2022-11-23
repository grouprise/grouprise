import locale
from calendar import different_locale
from hashlib import sha256

import boltons.strutils
import django.utils.text
import randomcolor
from django.conf import settings
from django.contrib.redirects.models import Redirect
from django.utils.translation import get_language, get_language_from_request, to_locale

from grouprise.core.settings import get_grouprise_site, CORE_SETTINGS


def slugify(value):
    # replace umlauts and other special characters with suitable representations
    ascii_value = boltons.strutils.asciify(value).decode()
    return django.utils.text.slugify(ascii_value)


def get_random_color():
    return randomcolor.RandomColor().generate(luminosity="dark")[0]


def get_accelerated_download_view(view, base_path):
    wrapper = CORE_SETTINGS.FILE_DOWNLOAD_WRAPPER
    if wrapper is None:
        return view
    else:
        return wrapper(
            view,
            source_url=base_path,
            # the webserver should be configured to deliver this path only for internal requests
            destination_url="/protected-downloads/",
        )


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


def add_redirect(old_path: str, new_path: str) -> None:
    redirect = Redirect.objects.create(
        site_id=get_grouprise_site().pk, old_path=old_path, new_path=new_path
    )
    redirect.save()


def hash_captcha_answer(value):
    answer = str(value).strip().lower()
    to_encode = (settings.SECRET_KEY + answer).encode()
    return sha256(to_encode).hexdigest()
