from django.apps import AppConfig


class MatrixChatConfig(AppConfig):
    name = "grouprise.features.matrix_chat"

    def ready(self):
        from .settings import MATRIX_SETTINGS

        MATRIX_SETTINGS.resolve_lazy_settings()
