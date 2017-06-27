from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^stadt/gestalten/$',
        views.List.as_view(),
        name='gestalten'),

    url(
        r'^stadt/gestalten/(?P<pk>[0-9]+)/edit/$',
        views.Update.as_view(),
        name='gestalt-update'),

    url(
        r'^stadt/gestalten/(?P<pk>[0-9]+)/edit/avatar/$',
        views.UpdateAvatar.as_view(),
        name='gestalt-avatar-update'),

    url(
        r'^stadt/gestalten/(?P<pk>[0-9]+)/edit/background/$',
        views.UpdateBackground.as_view(),
        name='gestalt-background-update'),

    url(
        r'^stadt/login/$',
        views.Login.as_view(),
        name='login'),
]
