from . import views
from django.conf import urls

urlpatterns = [
    urls.url(
        r'^group/(?P<group_pk>[0-9]+)/subscribe/$',
        views.GroupSubscribe.as_view(),
        name='group-subscribe'),

    urls.url(
        r'^group/(?P<group_pk>[0-9]+)/unsubscribe/$',
        views.GroupUnsubscribe.as_view(),
        name='group-unsubscribe'),
]
