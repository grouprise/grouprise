from django.conf import urls

from . import views

urlpatterns = [
    urls.url(
        r'^stadt/groups/$',
        views.List.as_view(),
        name='group-index'),

    urls.url(
        r'^stadt/groups/add/$',
        views.Create.as_view(),
        name='group-create'),

    urls.url(
        r'^stadt/groups/(?P<pk>[0-9]+)/edit$',
        views.Update.as_view(),
        name='group-update'),
]
