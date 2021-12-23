from grouprise.core.views import app_config

from .settings import GEO_SETTINGS


class GeoAppConfigMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if GEO_SETTINGS.ENABLED:
            app_config.add_setting(
                "geo",
                {
                    "tileServer": {
                        "url": GEO_SETTINGS.TILE_SERVER_URL,
                        "attribution": GEO_SETTINGS.TILE_SERVER_ATTRIBUTION,
                    },
                    "initialCenter": GEO_SETTINGS.LOCATION_SELECTOR_CENTER,
                    "initialZoom": GEO_SETTINGS.LOCATION_SELECTOR_ZOOM,
                },
            )

        return self.get_response(request)
