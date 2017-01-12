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

    urls.url(
        r'^groups/(?P<pk>[0-9]+)/edit$',
        views.Update.as_view(),
        name='group-update'),
]
