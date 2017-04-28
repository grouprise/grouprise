from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^(?P<entity_slug>[\w-]+)/polls/add/$',
        views.Create.as_view(),
        name='create-group-poll'),
]
