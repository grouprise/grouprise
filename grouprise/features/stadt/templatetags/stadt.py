from django import template
from django.conf import settings
from django.utils.translation import ugettext as _

register = template.Library()


@register.simple_tag()
def target_audience():
    return settings.GROUPRISE.get('TARGET_AUDIENCE', _('all'))
