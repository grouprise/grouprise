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
        r'^stadt/settings/group/$',
        views.Update.as_view(),
        name='group-settings'),

    urls.url(
        r'^stadt/settings/group/images/$',
        views.ImageUpdate.as_view(),
        name='group-image-settings'),
]
