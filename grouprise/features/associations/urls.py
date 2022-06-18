from django.urls import re_path

from grouprise.features.associations.views import Delete

urlpatterns = [
    re_path(
        r"^(?P<entity_slug>[\w.@+-]+)/(?P<association_slug>[\w-]+)/delete/$",
        Delete.as_view(),
        name="delete-association",
    ),
]
