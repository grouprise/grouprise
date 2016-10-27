from . import views
from django.conf import urls

urlpatterns = [
    urls.url(
        r'^groups/$',
        views.List.as_view(),
        name='group-index'),

    urls.url(
        r'^groups/add/$',
        views.Create.as_view(),
        name='group-create'),
]
