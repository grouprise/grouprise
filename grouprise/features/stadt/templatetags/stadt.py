from django import template
from django.conf import settings
from django.utils.translation import ugettext as _

register = template.Library()


@register.simple_tag()
def target_audience():
    # We cannot use grouprise.core.settings.CORE_SETTINGS here, since the default value needs to be
    # localized for each requester.
    try:
        return settings.GROUPRISE["TARGET_AUDIENCE"]
    except (KeyError, AttributeError):
        return _("all")
