from . import views
from django.conf import urls

urlpatterns = [
    urls.url(
        r'^(?P<entity_slug>[\w-]+)/(?P<association_slug>[\w-]+)/$',
        views.Content.as_view(),
        name='content'),

    urls.url(
        r'^(?P<entity_slug>[\w-]+)/(?P<association_slug>[\w-]+)/edit/$',
        views.CreateVersion.as_view(),
        name='create-content-version'),
]
