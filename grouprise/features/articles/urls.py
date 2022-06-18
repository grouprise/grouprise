from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r"^stadt/articles/$", views.List.as_view(), name="articles"),
    re_path(r"^stadt/articles/add/$", views.Create.as_view(), name="create-article"),
    re_path(
        r"^(?P<entity_slug>[\w.@+-]+)/articles/add/$",
        views.Create.as_view(),
        name="create-group-article",
    ),
]
