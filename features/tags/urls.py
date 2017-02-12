from . import views
from django.conf import urls

urlpatterns = [
    urls.url(
        r'^tags/(?P<slug>[-\w]+)/$',
        views.TagPage.as_view(),
        name='tag'),
]
