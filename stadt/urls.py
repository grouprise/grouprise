from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = [
    path('', include('core.urls')),

    path('', include('features.articles.urls')),
    path('', include('features.associations.urls')),
    path('', include('features.content.urls')),
    path('', include('features.contributions.urls')),
    path('', include('features.conversations.urls')),
    path('', include('features.events.urls')),
    path('', include('features.files.urls')),
    path('', include('features.galleries.urls')),
    path('', include('features.gestalten.urls')),
    path('', include('features.gestalten.auth.urls')),
    path('', include('features.groups.urls')),
    path('', include('features.memberships.urls')),
    path('', include('features.polls.urls')),
    path('', include('features.sharing.urls')),
    path('', include('features.subscriptions.urls')),
    path('', include('features.tags.urls')),

    path('', include('features.stadt.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
