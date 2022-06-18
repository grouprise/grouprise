from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r"^stadt/tags/(?P<slug>[-\w]+)/$", views.Detail.as_view(), name="tag"),
    re_path(
        r"^stadt/tags/(?P<slug>[-\w]+)/tag-group/$",
        views.TagGroup.as_view(),
        name="tag-group",
    ),
]
