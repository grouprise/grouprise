from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^stadt/galleries/add/$',
        views.Create.as_view(),
        name='create-gallery'),

    url(
        r'^(?P<entity_slug>[\w.@+-]+)/galleries/add/$',
        views.Create.as_view(),
        name='create-group-gallery'),
]
