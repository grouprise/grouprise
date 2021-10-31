from django import apps


class MembershipsConfig(apps.AppConfig):
    name = "grouprise.features.memberships"

    def ready(self):
        from . import signals  # noqa: F401
