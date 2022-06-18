from django.urls import re_path

from . import views

urlpatterns = [
    # This route is used in the content/_meta.html template. If there is a change in how
    # generated urls for this route work the meta urls should be checked afterwards.
    re_path(
        r"^stadt/content/(?P<association_pk>[0-9]+)/$",
        views.Permalink.as_view(),
        name="content-permalink",
    ),
    re_path(
        r"^(?P<entity_slug>[\w-]+)/(?P<association_slug>[\w-]+)/edit/$",
        views.Update.as_view(),
        name="update-content",
    ),
]
