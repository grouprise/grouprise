from . import models
from core import signals
from datetime import date
from django.conf import settings
from django.contrib.sites import models as sites_models
from django.core import urlresolvers


def set_group_meta(group):
    if not group.address:
        group.address = group.name
    if not group.date_founded:
        group.date_founded = date.today()
    if not group.url:
        group.url = '{protocol}://{domain}{path}'.format(
                protocol=settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL,
                domain=sites_models.Site.objects.get_current().domain,
                path=urlresolvers.reverse('group', args=[group.slug]),
                )
    group.save()


connections = [
    signals.connect_action(
        signals.model_created,
        set_group_meta,
        senders=[models.Group],
        ),
    ]
