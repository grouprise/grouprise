from . import views
from django.conf import urls

urlpatterns = [
    urls.url(r'^gestalt/(?P<pk>[0-9]+)/edit/$', views.GestaltUpdate.as_view(), name='gestalt-update'),
    urls.url(r'^group/membership/(?P<pk>[0-9]+)/delete/$', views.MembershipDelete.as_view(), name='membership-delete'),
    urls.url(r'^group/add/$', views.GroupCreate.as_view(), name='group-create'),
    urls.url(r'^group/(?P<pk>[0-9]+)/edit/$', views.GroupUpdate.as_view(), name='group-update'),
    urls.url(r'^group/(?P<group_pk>[0-9]+)/join/$', views.MembershipCreate.as_view(), name='membership-create'),
]
