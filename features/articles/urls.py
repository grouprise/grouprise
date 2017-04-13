from django.conf.urls import url

from features.content import views as content
from . import views

urlpatterns = [
    url(
        r'^stadt/articles/$',
        views.List.as_view(),
        name='articles'),

    url(
        r'^stadt/articles/add/$',
        content.Create.as_view(),
        name='create-article'),

    url(
        r'^(?P<entity_slug>[\w-]+)/articles/add/$',
        content.Create.as_view(),
        name='create-group-article'),
]
