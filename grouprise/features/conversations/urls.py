from . import views
from django.conf import urls

urlpatterns = [
    urls.url(
        r'^stadt/abuse/path=(?P<path>.*)$',
        views.CreateAbuseConversation.as_view(),
        name='abuse'),

    urls.url(
        r'^stadt/conversations/(?P<association_pk>[0-9]+)/$',
        views.Conversation.as_view(),
        name='conversation'),

    urls.url(
        r'^stadt/gestalten/(?P<gestalt_pk>[0-9]+)/conversations/add/$',
        views.CreateGestaltConversation.as_view(),
        name='create-gestalt-conversation'),

    urls.url(
        r'^stadt/groups/(?P<group_pk>[0-9]+)/conversations/$',
        views.GroupConversations.as_view(),
        name='group-conversations'),

    urls.url(
        r'^stadt/groups/(?P<group_pk>[0-9]+)/conversations/add/$',
        views.CreateGroupConversation.as_view(),
        name='create-group-conversation'),
]
