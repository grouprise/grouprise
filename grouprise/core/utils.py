import asyncio
import codecs
import locale
import threading
from calendar import different_locale

import django.utils.text
import randomcolor
import translitcodec  # noqa: F401, used indirectly via "translit/"
from django.contrib.redirects.models import Redirect
from django.utils.translation import get_language, get_language_from_request, to_locale

from grouprise.core.settings import get_grouprise_site, CORE_SETTINGS


def slugify(value):
    return django.utils.text.slugify(codecs.encode(value, "translit/long"))


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


def run_async(async_func):
    """run an async callable in a new loop (if there is no running loop) or in a separate thread

    The result of the async callable is returned.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        # there is a running loop (probably we are within a huey task)
        result = []
        # execute the function in a separate thread (nested loops are not supported in Python)
        thread = threading.Thread(target=lambda: result.append(asyncio.run(async_func)))
        thread.start()
        thread.join()
        return result[0]
    else:
        # no loop is running: create a new one
        return asyncio.run(async_func)
