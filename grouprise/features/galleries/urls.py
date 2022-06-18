from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r"^stadt/galleries/add/$", views.Create.as_view(), name="create-gallery"),
    re_path(
        r"^(?P<entity_slug>[\w.@+-]+)/galleries/add/$",
        views.Create.as_view(),
        name="create-group-gallery",
    ),
]
