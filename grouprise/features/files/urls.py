from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^(?P<entity_slug>[\w.@+-]+)/files/add/$',
        views.Create.as_view(),
        name='create-group-file'),
]
