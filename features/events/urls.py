from . import views
from django.conf import urls

urlpatterns = [
    urls.url(
        r'^events/$',
        views.List.as_view(),
        name='events'),
]
