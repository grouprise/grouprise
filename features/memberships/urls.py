from . import views
from django.conf import urls

urlpatterns = [
    urls.url(
        r'^group/(?P<group_pk>[0-9]+)/join/$',
        views.Join.as_view(),
        name='join'),

    urls.url(
        r'^group/(?P<group_pk>[0-9]+)/members/$',
        views.Members.as_view(),
        name='members'),

    urls.url(
        r'^group/(?P<group_pk>[0-9]+)/resign/$',
        views.Resign.as_view(),
        name='resign'),
]
