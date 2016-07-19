from . import views
from django.conf import urls

urlpatterns = [
    urls.url(
        r'^group/(?P<group_pk>[0-9]+)/join/$',
        views.Join.as_view(),
        name='join'),
]
