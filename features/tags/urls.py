from . import views
from django.conf.urls import url

urlpatterns = [
    url(
        r'^stadt/tags/(?P<slug>[-\w]+)/$',
        views.Detail.as_view(),
        name='tag'),

    url(
        r'^stadt/tags/(?P<slug>[-\w]+)/tag-group$',
        views.TagGroup.as_view(),
        name='tag-group'),
]
