import rules

from .settings import GEO_SETTINGS


@rules.predicate
def is_geo_enabled():
    return GEO_SETTINGS.ENABLED


rules.add_rule("is_geo_enabled", is_geo_enabled)
