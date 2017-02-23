from . import views
from django.conf import urls

urlpatterns = [
    urls.url(
        r'^gestalten/$',
        views.List.as_view(),
        name='gestalten'),
]
