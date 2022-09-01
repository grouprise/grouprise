from django.conf.urls import url

from grouprise.features.associations.views import Delete

urlpatterns = [
    url(
        r"^(?P<entity_slug>[\w.@+-]+)/(?P<association_slug>[\w-]+)/delete/$",
        Delete.as_view(),
        name="delete-association",
    ),
]
