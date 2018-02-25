from django.conf.urls import url

from . import views, rest_api

urlpatterns = [
    url(
        r'^stadt/polls/add/$',
        views.Create.as_view(),
        name='create-poll'),

    url(
        r'^(?P<entity_slug>[\w-]+)/polls/add/$',
        views.Create.as_view(),
        name='create-group-poll'),

    url(
        r'^(?P<entity_slug>[\w-]+)/(?P<association_slug>[\w-]+)/vote/$',
        views.Vote.as_view(),
        name='vote'),
    url(r'^stadt/api/polls/(?P<pk>[^/.]+)/vote', rest_api.vote, name='polls-vote'),
]
