from django.apps import AppConfig


class MatrixChatConfig(AppConfig):
    name = "grouprise.features.matrix_chat"

    def ready(self):
        from .settings import MATRIX_SETTINGS

        try:
            MATRIX_SETTINGS.resolve_lazy_settings()
        except Exception:
            # This may fail during the initial "migrate" operation due to the missing "site".
            pass
