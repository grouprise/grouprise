from . import views
from django.conf import urls

urlpatterns = [
    urls.url(
        r'^articles/$',
        views.List.as_view(),
        name='articles'),
]
