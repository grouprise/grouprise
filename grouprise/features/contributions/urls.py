from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r"stadt/associations/(?P<association_pk>[0-9]+)/contributions/"
        r"(?P<contribution_pk>[0-9]+)/reply-to-author/$",
        views.ReplyToAuthor.as_view(),
        name="reply-to-author",
    ),
    url(
        r"(?P<entity_slug>[\w-]+)/(?P<association_slug>[\w-]+)/contributions/"
        r"(?P<pk>[0-9]+)/delete/$",
        views.Delete.as_view(),
        name="delete-contribution",
    ),
]
