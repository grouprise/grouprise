from django.conf.urls import url

from .settings import MATRIX_SETTINGS


if MATRIX_SETTINGS.ENABLED:
    from . import views

    urlpatterns = [
        url(
            r"^stadt/settings/matrix-chat/$",
            views.UpdateMatrixChatGestaltSettings.as_view(),
            name="matrix-chat-settings",
        ),
    ]
else:
    urlpatterns = []
