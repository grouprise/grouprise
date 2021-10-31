import django.apps
from django.urls import include, path, re_path
from django.conf.urls import url

from grouprise.features.content.views import Detail as AssociationDetailView
from grouprise.features.stadt.views import Help
from . import feeds, views


urlpatterns = [
    url(r"^$", views.Index.as_view(), name="index"),
    url(r"^stadt/feed/$", feeds.IndexFeed(), name="feed"),
    url(
        r"^stadt/groups/(?P<group_pk>[0-9]+)/feed/$",
        feeds.GroupFeed(),
        name="group-feed",
    ),
    path("stadt/help/", Help.as_view(), name="help"),
    url(r"^stadt/privacy/$", views.Privacy.as_view(), name="privacy"),
    url(r"^stadt/search/$", views.Search.as_view(), name="search"),
    url(r"^(?P<entity_slug>[\w-]+)/$", views.Entity.as_view(), name="entity"),
    re_path(
        r"^(?P<entity_slug>[\w-]+)/(?P<association_slug>[\w-]+)/$",
        AssociationDetailView.as_view(),
        name="content",
    ),
]

if django.apps.apps.is_installed("oauth2_provider"):
    urlpatterns.append(
        path(
            "stadt/oauth/", include("oauth2_provider.urls", namespace="oauth2_provider")
        )
    )
