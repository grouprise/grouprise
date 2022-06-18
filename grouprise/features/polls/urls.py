from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r"^stadt/polls/add/$", views.Create.as_view(), name="create-poll"),
    re_path(
        r"^(?P<entity_slug>[\w-]+)/polls/add/$",
        views.Create.as_view(),
        name="create-group-poll",
    ),
    re_path(
        r"^(?P<entity_slug>[\w-]+)/(?P<association_slug>[\w-]+)/vote/$",
        views.Vote.as_view(),
        name="vote",
    ),
]
