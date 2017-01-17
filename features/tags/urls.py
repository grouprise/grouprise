from . import views
from django.conf import urls

urlpatterns = [
    urls.url(
        r'^tags/(?P<pk>[0-9]+)/$',
        views.Tag.as_view(),
        name='tag'),
]
