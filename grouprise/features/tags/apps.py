from django import apps


class TagsConfig(apps.AppConfig):
    name = "grouprise.features.tags"

    def ready(self):
        # register markdown extensions
        import grouprise.features.tags.markdown  # noqa: F401

        # build tag configuration from settings
        from . import signals

        signals.Index.build()
