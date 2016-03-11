from . import views
from django.conf import urls

urlpatterns = [
    urls.url(r'^stadt/content/add/(?:group=(?P<group_slug>[\w-]+))?$', views.ContentCreate.as_view(), name='content-create'),
    urls.url(r'^stadt/content/(?P<pk>[0-9]+)/edit/(?:group=(?P<group_slug>[\w-]+))?$', views.ContentUpdate.as_view(), name='content-update'),
    urls.url(r'^stadt/event/(?P<year>[0-9]{4})/(?P<month>[-\w]+)/(?P<day>[0-9]+)/$', views.EventDay.as_view(), name='event-day'),
]
