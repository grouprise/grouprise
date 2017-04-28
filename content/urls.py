from . import views
from django.conf import urls


urlpatterns = [
    urls.url(
        r'^content/(?P<content_pk>[0-9]+)/image/$',
        views.ImageList.as_view(),
        name='content-image-list'),
    urls.url(
        r'^event/(?P<year>[0-9]{4})/(?P<month>[-\w]+)/(?P<day>[0-9]+)/$',
        views.EventDay.as_view(),
        name='event-day'),
    urls.url(r'^markdown/$', views.Markdown.as_view(), name='markdown'),
]
