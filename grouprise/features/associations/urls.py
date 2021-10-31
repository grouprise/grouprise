from django.urls import path
from django.conf.urls import url

from grouprise.features.associations.views import ActivityView, Delete

urlpatterns = [
    path("stadt/activity", ActivityView.as_view(), name="activity"),
    url(
        r"^(?P<entity_slug>[\w.@+-]+)/(?P<association_slug>[\w-]+)/delete/$",
        Delete.as_view(),
        name="delete-association",
    ),
]
