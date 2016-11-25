from . import views
from django.conf import urls

urlpatterns = [
    urls.url(
        r'^conversations/(?P<association_pk>[0-9]+)/$',
        views.Conversation.as_view(),
        name='conversation'),
]
