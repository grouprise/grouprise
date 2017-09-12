from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^(?P<entity_slug>[\w.@+-]+)/(?P<association_slug>[\w-]+)/note/$',
        views.Create.as_view(),
        name='create-note',
    ),
]
