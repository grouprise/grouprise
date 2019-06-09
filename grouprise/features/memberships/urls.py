from django.conf import urls
from django.urls import path

from grouprise.features.memberships import views
from grouprise.features.memberships.views import Join

urlpatterns = [
    path('<slug:group>/actions/join', Join.as_view(), name='join'),
    urls.url(
        r'^stadt/groups/join/confirm/(?P<secret_key>[a-z0-9]+)/$',
        views.JoinConfirm.as_view(),
        name='join-confirm'
    ),
    urls.url(
        r'^(?P<group_slug>[\w-]+)/join/request/$',
        views.JoinRequest.as_view(),
        name='join-request'
    ),
    urls.url(
        r'^stadt/groups/(?P<group_pk>[0-9]+)/members/$',
        views.Members.as_view(),
        name='members'),

    urls.url(
        r'^stadt/groups/(?P<group_pk>[0-9]+)/members/add/$',
        views.MemberAdd.as_view(),
        name='member-create'),

    urls.url(
        r'^stadt/groups/(?P<group_pk>[0-9]+)/resign/$',
        views.Resign.as_view(),
        name='resign'
    ),
    urls.url(
        r'^stadt/groups/resign/confirm/(?P<secret_key>[a-z0-9]+)/$',
        views.ResignConfirm.as_view(),
        name='resign-confirm'
    ),
    urls.url(
        r'^stadt/groups/(?P<group_pk>[0-9]+)/resign/request/$',
        views.ResignRequest.as_view(),
        name='resign-request'
    ),
    urls.url(
        r'^stadt/associations/(?P<association_pk>[0-9]+)/apply/$',
        views.Apply.as_view(),
        name='create-membership-application'),

    urls.url(
        r'^stadt/memberships/applications/(?P<application_pk>[0-9]+)/accept/$',
        views.AcceptApplication.as_view(),
        name='accept-membership-application'),
]
