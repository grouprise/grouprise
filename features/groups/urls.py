from django.conf import urls

from . import views

urlpatterns = [
    urls.url(
        r'^stadt/groups/$',
        views.List.as_view(),
        name='group-index'),

    urls.url(
        r'^stadt/groups/add/$',
        views.Create.as_view(),
        name='group-create'),

    urls.url(
        r'^stadt/settings/group/$',
        views.Update.as_view(),
        name='group-settings'),

    urls.url(
        r'^stadt/groups/(?P<pk>[0-9]+)/edit/avatar/$',
        views.GroupAvatarUpdate.as_view(),
        name='group-avatar-update'),

    urls.url(
        r'^stadt/groups/(?P<pk>[0-9]+)/edit/logo/$',
        views.GroupLogoUpdate.as_view(),
        name='group-logo-update'),
]
