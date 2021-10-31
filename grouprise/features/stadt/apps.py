from django import apps


class StadtConfig(apps.AppConfig):
    name = "grouprise.features.stadt"

    def ready(self):
        # register markdown extensions
        import grouprise.features.stadt.markdown  # noqa: F401
