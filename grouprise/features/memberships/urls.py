from django.urls import path, re_path

from grouprise.features.memberships import views
from grouprise.features.memberships.views import Join

urlpatterns = [
    path("<slug:group>/actions/join", Join.as_view(), name="join"),
    re_path(
        r"^stadt/groups/join/confirm/(?P<secret_key>[a-z0-9]+)/$",
        views.JoinConfirm.as_view(),
        name="join-confirm",
    ),
    re_path(
        r"^(?P<group_slug>[\w-]+)/join/request/$",
        views.JoinRequest.as_view(),
        name="join-request",
    ),
    re_path(
        r"^stadt/groups/(?P<group_pk>[0-9]+)/members/$",
        views.Members.as_view(),
        name="members",
    ),
    re_path(
        r"^stadt/groups/(?P<group_pk>[0-9]+)/members/add/$",
        views.MemberAdd.as_view(),
        name="member-create",
    ),
    re_path(
        r"^stadt/groups/(?P<group_pk>[0-9]+)/resign/$",
        views.Resign.as_view(),
        name="resign",
    ),
    re_path(
        r"^stadt/groups/resign/confirm/(?P<secret_key>[a-z0-9]+)/$",
        views.ResignConfirm.as_view(),
        name="resign-confirm",
    ),
    re_path(
        r"^stadt/groups/(?P<group_pk>[0-9]+)/resign/request/$",
        views.ResignRequest.as_view(),
        name="resign-request",
    ),
    re_path(
        r"^stadt/associations/(?P<association_pk>[0-9]+)/apply/$",
        views.Apply.as_view(),
        name="create-membership-application",
    ),
    re_path(
        r"^stadt/memberships/applications/(?P<application_pk>[0-9]+)/accept/$",
        views.AcceptApplication.as_view(),
        name="accept-membership-application",
    ),
]
