from django.conf.urls import url

import entities
from features.content import views as content

urlpatterns = [
    url(
        r'^$',
        content.List.as_view(template_name='stadt/index.html'),
        name='index',
    ),

    url(
        r'^(?P<gestalt_slug>[\w.@+-]+)/$',
        entities.views.Gestalt.as_view(),
        name='gestalt'),

    url(
        r'^(?P<group_slug>[\w-]+)/$',
        entities.views.Group.as_view(),
        name='group'),
]
