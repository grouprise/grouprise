import html
import os
import re

import html2text as python_html2text
from django import template
from django.conf import settings
from django.contrib.sites import models as sites_models

from . import Link

register = template.Library()

HAS_HTTP_PROTOCOL_REGEX = re.compile(r'^https?://')


@register.filter
def filename(value, include_ext=True):
    """Split the filename off the given path."""
    base = os.path.basename(getattr(value, 'name', value))
    return base if include_ext else os.path.splitext(base)[0]


@register.filter
def endswith(value: str, search):
    return value.endswith(search)


@register.filter
def startswith(value: str, search):
    return value.startswith(search)


@register.filter
def cuttrailing(s1, s2):
    """Remove a string at the end of a string."""
    if s1.endswith(s2):
        return s1[:-len(s2)]
    return s1


@register.filter
def nolinebreaks(value):
    """Replace line breaks by spaces."""
    return ' '.join(str(value).split('\n'))


@register.filter
def link_to(text, url):
    """Combine text and url to a link tuple."""
    return Link(text=text, url=url)


@register.filter
def url_for_user(model, user):
    "Return the result of get_absolute_url_for_user()."""
    return model.get_absolute_url_for_user(user)


def _get_baseurl():
    return '{proto}://{domain}'.format(
            proto=settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL,
            domain=sites_models.Site.objects.get_current().domain)


@register.filter
def html2text(html_text, preset='mail'):
    text_maker = python_html2text.HTML2Text(baseurl=_get_baseurl())
    text_maker.body_width = 0
    if preset == 'mail':
        text_maker.inline_links = False
        text_maker.links_each_paragraph = True
        text_maker.use_automatic_links = True
        text_maker.ignore_images = True
    elif preset == 'import':
        text_maker.escape_snob = True
    return html.unescape(text_maker.handle(html_text)).rstrip()


@register.filter
def full_url(path):
    if HAS_HTTP_PROTOCOL_REGEX.match(path) is not None:
        # path already is an absolute URL
        return path
    else:
        return '{baseurl}{path}'.format(baseurl=_get_baseurl(), path=path)
