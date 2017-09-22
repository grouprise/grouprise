from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'stadt/contributions/(?P<pk>[0-9]+)/delete/$',
        views.Delete.as_view(),
        name='delete-contribution',
    )
]
