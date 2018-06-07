from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^stadt/groups/(?P<group_pk>[0-9]+)/subscribe/$',
        views.GroupSubscribe.as_view(),
        name='group-subscribe',
    ),
    url(
        r'^stadt/groups/(?P<group_pk>[0-9]+)/unsubscribe/$',
        views.GroupUnsubscribe.as_view(),
        name='group-unsubscribe',
    ),
    url(
        r'^stadt/groups/(?P<group_pk>[0-9]+)/unsubscribe/request/$',
        views.GroupUnsubscribeRequest.as_view(),
        name='group-unsubscribe-request',
    ),
]
