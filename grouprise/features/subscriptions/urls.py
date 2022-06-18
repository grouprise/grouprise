from django.urls import path, re_path

from grouprise.features.subscriptions import views
from grouprise.features.subscriptions.views import GroupSubscribe

urlpatterns = [
    path(
        "<slug:group>/actions/subscribe",
        GroupSubscribe.as_view(),
        name="group-subscribe",
    ),
    re_path(
        r"^stadt/groups/(?P<group_pk>[0-9]+)/unsubscribe/$",
        views.GroupUnsubscribe.as_view(),
        name="group-unsubscribe",
    ),
    re_path(
        r"^stadt/groups/(?P<group_pk>[0-9]+)/unsubscribe/request/$",
        views.GroupUnsubscribeRequest.as_view(),
        name="group-unsubscribe-request",
    ),
    re_path(
        r"^stadt/unsubscribe/confirm/(?P<secret_key>[a-z0-9]+)/$",
        views.GroupUnsubscribeConfirm.as_view(),
        name="group-unsubscribe-confirm",
    ),
]
