from django.urls import re_path

from . import views

urlpatterns = [
    re_path(
        r"^stadt/abuse/path=(?P<path>.*)$",
        views.CreateAbuseConversation.as_view(),
        name="abuse",
    ),
    re_path(
        r"^stadt/conversations/(?P<association_pk>[0-9]+)/$",
        views.Conversation.as_view(),
        name="conversation",
    ),
    re_path(
        r"^stadt/gestalten/(?P<gestalt_pk>[0-9]+)/conversations/add/$",
        views.CreateGestaltConversation.as_view(),
        name="create-gestalt-conversation",
    ),
    re_path(
        r"^stadt/groups/(?P<group_pk>[0-9]+)/conversations/$",
        views.GroupConversations.as_view(),
        name="group-conversations",
    ),
    re_path(
        r"^stadt/groups/(?P<group_pk>[0-9]+)/conversations/add/$",
        views.CreateGroupConversation.as_view(),
        name="create-group-conversation",
    ),
]
