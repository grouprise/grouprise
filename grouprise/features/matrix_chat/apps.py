from django.apps import AppConfig
from huey.contrib.djhuey import on_startup


@on_startup()
def _resolve_lazy_matrix_settings():
    """we need to ensure, that all settings are resolved (required for async tasks)

    Django (at least up to 4.x) does not allow ORM requests in async contexts.
    """
    from .settings import MATRIX_SETTINGS

    MATRIX_SETTINGS.resolve_lazy_settings()


class MatrixChatConfig(AppConfig):
    name = "grouprise.features.matrix_chat"

    def ready(self):
        from .settings import MATRIX_SETTINGS

        try:
            MATRIX_SETTINGS.resolve_lazy_settings()
        except Exception:
            # This may fail during the initial "migrate" operation due to the missing "site".
            pass
