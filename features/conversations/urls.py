from . import views
from django.conf import urls

urlpatterns = [
    urls.url(
        r'^conversations/(?P<association_pk>[0-9]+)/$',
        views.Conversation.as_view(),
        name='conversation'),

    urls.url(
        r'^groups/(?P<group_pk>[0-9]+)/conversations/add/$',
        views.CreateConversation.as_view(),
        name='message-create'),
]
