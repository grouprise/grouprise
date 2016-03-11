from . import views
from django.conf import urls

urlpatterns = [
    urls.url(r'^stadt/gestalt/(?P<pk>[0-9]+)/edit/$', views.GestaltUpdate.as_view(), name='gestalt-update'),
    urls.url(r'^stadt/group/membership/add/group=(?P<group_slug>[\w-]+)$', views.GroupMembershipCreate.as_view(), name='group-membership-create'),
    urls.url(r'^stadt/group/membership/(?P<pk>[0-9]+)/delete/$', views.GroupMembershipDelete.as_view(), name='group-membership-delete'),
    urls.url(r'^stadt/group/new/$', views.GroupCreate.as_view(), name='group-create'),
    urls.url(r'^stadt/group/(?P<pk>[0-9]+)/edit/$', views.GroupUpdate.as_view(), name='group-update'),
]
