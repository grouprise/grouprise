from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'(?P<entity_slug>[\w.@+-]+)/(?P<association_slug>[\w-]+)/contributions/'
        r'(?P<pk>[0-9]+)/delete/$',
        views.Delete.as_view(),
        name='delete-contribution',
    )
]
