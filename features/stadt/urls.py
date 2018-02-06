from django.conf.urls import include, url

from . import feeds, views

urlpatterns = [
    url(
        r'^$',
        views.Index.as_view(),
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
        r'^stadt/privacy/$',
        views.Privacy.as_view(),
        name='privacy'),

    url(r'^stadt/search/$', views.Search.as_view(), name='search'),

    url(
        r'^(?P<entity_slug>[\w-]+)/$',
        views.Entity.as_view(),
        name='entity'),
]
