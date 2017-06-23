from django.conf.urls import url

from features.content import views as content
from . import views

urlpatterns = [
    url(
        r'^$',
        content.List.as_view(template_name='stadt/index.html'),
        name='index'),

    url(
        r'^(?P<entity_slug>[\w.@+-]+)/$',
        views.Entity.as_view(),
        name='entity'),
]
