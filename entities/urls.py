from . import views
from content import creation as content_creation
from django.conf import urls


urlpatterns = [
    urls.url(
        r'^abuse/path=(?P<path>.*)',
        content_creation.AbuseMessage.as_view(),
        name='abuse'),
    urls.url(r'^gestalt/$', views.GestaltList.as_view(), name='gestalt-index'),
    urls.url(
        r'^gestalt/(?P<pk>[0-9]+)/edit/$',
        views.GestaltUpdate.as_view(),
        name='gestalt-update'),
    urls.url(
        r'^gestalt/(?P<pk>[0-9]+)/edit/avatar/$',
        views.GestaltAvatarUpdate.as_view(),
        name='gestalt-avatar-update'),
    urls.url(
        r'^gestalt/(?P<pk>[0-9]+)/edit/background/$',
        views.GestaltBackgroundUpdate.as_view(),
        name='gestalt-background-update'),
    urls.url(
        r'^gestalt/(?P<gestalt_pk>[0-9]+)/contact/$',
        content_creation.GestaltMessage.as_view(),
        name='gestalt-message-create'),
    urls.url(r'^group/(?P<pk>[0-9]+)/edit/$', views.GroupUpdate.as_view(), name='group-update'),
    urls.url(
        r'^group/(?P<pk>[0-9]+)/edit/avatar/$',
        views.GroupAvatarUpdate.as_view(),
        name='group-avatar-update'),
    urls.url(
        r'^group/(?P<pk>[0-9]+)/edit/logo/$',
        views.GroupLogoUpdate.as_view(),
        name='group-logo-update'),
    urls.url(r'^imprint/$', views.Imprint.as_view(), name='imprint'),
    urls.url(r'^privacy/$', views.Privacy.as_view(), name='privacy'),
]
