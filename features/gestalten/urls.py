from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^stadt/gestalten/$',
        views.List.as_view(),
        name='gestalten'),

    url(
        r'^stadt/gestalten/(?P<pk>[0-9]+)/edit/$',
        views.GestaltUpdate.as_view(),
        name='gestalt-update'),

    url(
        r'^stadt/gestalten/(?P<pk>[0-9]+)/edit/avatar/$',
        views.GestaltAvatarUpdate.as_view(),
        name='gestalt-avatar-update'),

    url(
        r'^stadt/gestalten/(?P<pk>[0-9]+)/edit/background/$',
        views.GestaltBackgroundUpdate.as_view(),
        name='gestalt-background-update'),
]
