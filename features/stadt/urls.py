from django.conf.urls import url

from features.content import views as content
from . import feeds, views

urlpatterns = [
    url(
        r'^$',
        content.List.as_view(template_name='stadt/index.html'),
        name='index'),

    url(
        r'^stadt/feed/$',
        feeds.Index(),
        name='feed'),

    url(
        r'^stadt/groups/(?P<group_pk>[0-9]+)/feed/$',
        feeds.Group(),
        name='group-feed'),

    url(
        r'^stadt/imprint/$',
        views.Imprint.as_view(),
        name='imprint'),

    url(
        r'^stadt/privacy/$',
        views.Privacy.as_view(),
        name='privacy'),

    url(
        r'^(?P<entity_slug>[\w-]+)/$',
        views.Entity.as_view(),
        name='entity'),
]
