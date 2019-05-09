from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^(?P<entity_slug>[\w.@+-]+)/(?P<association_slug>[\w-]+)/delete/$',
        views.Delete.as_view(),
        name='delete-association',
    ),
]
