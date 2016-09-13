from django.contrib.sites import shortcuts
from django.conf import settings


def site(request):
    return {'site': shortcuts.get_current_site(request)}


def assets(request):
    return {'asset_version': settings.ASSET_VERSION }
