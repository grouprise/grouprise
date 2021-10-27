from django.conf.urls import url

from .settings import MATRIX_SETTINGS


if MATRIX_SETTINGS.ENABLED:
    from . import views

    urlpatterns = [
        url(
            r"^stadt/settings/matrix-chat/$",
            views.UpdateMatrixChatGestaltSettings.as_view(),
            name="matrix-chat-settings-user",
        ),
        url(
            r"^stadt/settings/group/matrix-chat/$",
            views.UpdateMatrixChatGroupSettings.as_view(),
            name="matrix-chat-settings-group",
        ),
        url(
            r"^stadt/help/matrix-chat/$",
            views.ShowMatrixChatHelp.as_view(),
            name="help-matrix-chat",
        ),
        url(
            r"^(?P<group_slug>[\w-]+)/-/chat/public/$",
            views.RedirectToMatrixRoomGroupPublic.as_view(),
            name="matrix-chat-room-group-public",
        ),
        url(
            r"^(?P<group_slug>[\w-]+)/-/chat/private/$",
            views.RedirectToMatrixRoomGroupPrivate.as_view(),
            name="matrix-chat-room-group-private",
        ),
    ]
else:
    urlpatterns = []
