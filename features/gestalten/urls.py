from django.conf import urls

import entities.views
import features.events.views
import features.gestalten.views

urlpatterns = [
    urls.url(
        r'^stadt/gestalten/$',
        features.gestalten.views.List.as_view(),
        name='gestalten'),

    urls.url(
        r'^gestalt/(?P<gestalt_slug>[\w.@+-]+)/$',
        entities.views.Gestalt.as_view(),
        name='gestalt'),
]
