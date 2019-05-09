from . import views
from django.conf import urls

urlpatterns = [
    urls.url(
        r'^stadt/groups/(?P<group_pk>[0-9]+)/invite/$',
        views.MemberInvite.as_view(),
        name='member-invite'),

    urls.url(
        r'^stadt/groups/(?P<group_pk>[0-9]+)/recommend/$',
        views.GroupRecommend.as_view(),
        name='group-recommend'),
]
