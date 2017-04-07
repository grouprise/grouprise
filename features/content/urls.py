from . import views
from django.conf import urls

urlpatterns = [
    urls.url(
        r'^$',
        views.List.as_view(),
        name='list-content'),

    urls.url(
        r'^(?P<entity_slug>[\w-]+)/(?P<association_slug>[\w-]+)/$',
        views.Content.as_view(),
        name='content'),

    urls.url(
        r'^stadt/articles/add/$',
        views.Create.as_view(),
        name='create-content'),

    urls.url(
        r'^(?P<entity_slug>[\w-]+)/articles/add/$',
        views.Create.as_view(),
        name='create-group-content'),

    urls.url(
        r'^(?P<entity_slug>[\w-]+)/(?P<association_slug>[\w-]+)/edit/$',
        views.Update.as_view(),
        name='update-content'),
]
