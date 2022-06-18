from django.urls import re_path

from .settings import MATRIX_SETTINGS

if MATRIX_SETTINGS.ENABLED:
    from . import views

    urlpatterns = [
        re_path(
            r"^stadt/settings/matrix-chat/$",
            views.UpdateMatrixChatGestaltSettings.as_view(),
            name="matrix-chat-settings-user",
        ),
        re_path(
            r"^stadt/settings/group/matrix-chat/$",
            views.UpdateMatrixChatGroupSettings.as_view(),
            name="matrix-chat-settings-group",
        ),
        re_path(
            r"^stadt/help/matrix-chat/$",
            views.ShowMatrixChatHelp.as_view(),
            name="help-matrix-chat",
        ),
        re_path(
            r"^(?P<group_slug>[\w-]+)/-/chat/public/$",
            views.RedirectToMatrixRoomGroupPublic.as_view(),
            name="matrix-chat-room-group-public",
        ),
        re_path(
            r"^(?P<group_slug>[\w-]+)/-/chat/private/$",
            views.RedirectToMatrixRoomGroupPrivate.as_view(),
            name="matrix-chat-room-group-private",
        ),
        re_path(
            r"^stadt/chat/.*$",
            views.ShowMissingWebClientWarning.as_view(),
            name="matrix-chat-client-missing",
        ),
        re_path(
            r"^stadt/chat-rooms/public-feed/$",
            views.RedirectToMatrixRoomPublicFeed.as_view(),
            name="matrix-chat-public-feed",
        ),
    ]
else:
    urlpatterns = []
