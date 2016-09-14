from django.contrib.sites import shortcuts
from django.conf import settings


def site(request):
    return {
        'site': shortcuts.get_current_site(request),
        'site_description': 'Stadtgestalten ist eine neue Internet-Plattform und ermöglicht aktiven, engagierten '
                            'Menschen und Gruppen in der Stadt, sich unkompliziert zu informieren, zu präsentieren '
                            'und miteinander zu vernetzen.',
        'http_origin': request.build_absolute_uri("/").rstrip("/")
    }


def assets(request):
    return {'asset_version': settings.ASSET_VERSION }
