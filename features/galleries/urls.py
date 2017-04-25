from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^(?P<entity_slug>[\w-]+)/galleries/add/$',
        views.Create.as_view(),
        name='create-group-gallery'),
]
