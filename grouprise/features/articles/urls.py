from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^stadt/articles/$", views.List.as_view(), name="articles"),
    url(r"^stadt/articles/add/$", views.Create.as_view(), name="create-article"),
    url(
        r"^(?P<entity_slug>[\w.@+-]+)/articles/add/$",
        views.Create.as_view(),
        name="create-group-article",
    ),
]
