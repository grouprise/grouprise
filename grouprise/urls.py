from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = []

try:
    extra_urls = settings.GROUPRISE_URLS
except AttributeError:
    pass
else:
    urlpatterns += [
        path(key, include(module_path)) for key, module_path in extra_urls.items()
    ]

urlpatterns += [
    path("", include("grouprise.core.urls")),
    path("", include("grouprise.features.articles.urls")),
    path("", include("grouprise.features.associations.urls")),
    path("", include("grouprise.features.builtin_inbox_notifications.urls")),
    path("", include("grouprise.features.content.urls")),
    path("", include("grouprise.features.contributions.urls")),
    path("", include("grouprise.features.conversations.urls")),
    path("", include("grouprise.features.events.urls")),
    path("", include("grouprise.features.files.urls")),
    path("", include("grouprise.features.galleries.urls")),
    path("", include("grouprise.features.geo.urls")),
    path("", include("grouprise.features.gestalten.urls")),
    path("", include("grouprise.features.gestalten.auth.urls")),
    path("", include("grouprise.features.groups.urls")),
    path("", include("grouprise.features.images.urls")),
    path("", include("grouprise.features.matrix_chat.urls")),
    path("", include("grouprise.features.memberships.urls")),
    path("", include("grouprise.features.polls.urls")),
    path("", include("grouprise.features.rest_api.urls")),
    path("", include("grouprise.features.subscriptions.urls")),
    path("", include("grouprise.features.tags.urls")),
    path("", include("grouprise.features.stadt.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
