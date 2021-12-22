from django.conf import settings

from grouprise.core.settings import LazySettingsResolver

try:
    _GEO_SETTINGS = settings.GROUPRISE["GEO"]
except (KeyError, AttributeError):
    _GEO_SETTINGS = {}


GEO_SETTINGS = LazySettingsResolver(
    ENABLED=_GEO_SETTINGS.get("ENABLED", False),
    # The tile server default is defined in grouprise.settings_loader
    # because it adds a CSP exemption.
    TILE_SERVER_URL=_GEO_SETTINGS.get("TILE_SERVER", {}).get("URL", None),
    TILE_SERVER_ATTRIBUTION=_GEO_SETTINGS.get("TILE_SERVER", {}).get(
        "ATTRIBUTION",
        (
            "&copy; <a target='_blank' href='https://osm.org/copyright'>"
            "OpenStreetMap</a> contributors"
        ),
    ),
    LOCATION_SELECTOR_CENTER=_GEO_SETTINGS.get("LOCATION_SELECTOR", {}).get(
        "CENTER",
        [
            # this is germany :)
            [55.0846, 8.3174],
            [47.271679, 10.174047],
            [51.0525, 5.866944],
            [51.27291, 15.04193],
        ],
    ),
    LOCATION_SELECTOR_ZOOM=_GEO_SETTINGS.get("LOCATION_SELECTOR", {}).get("ZOOM", None),
)
