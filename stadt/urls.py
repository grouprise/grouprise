from django.conf import settings, urls
from django.conf.urls import static
from django.contrib import admin

urlpatterns = [
    urls.url(r'^', urls.include('core.urls')),
    urls.url(r'^stadt/admin/', admin.site.urls),
    urls.url(r'^stadt/api/', urls.include('core.api_urls')),

    urls.url(r'^stadt/', urls.include('account.urls')),
    urls.url(r'^stadt/', urls.include('features.associations.urls')),
    urls.url(r'^stadt/', urls.include('features.conversations.urls')),
    urls.url(r'^stadt/', urls.include('features.memberships.urls')),
    urls.url(r'^stadt/', urls.include('features.sharing.urls')),
    urls.url(r'^stadt/', urls.include('features.subscriptions.urls')),

    urls.url(r'^', urls.include('features.articles.urls')),
    urls.url(r'^', urls.include('features.contributions.urls')),
    urls.url(r'^', urls.include('features.events.urls')),
    urls.url(r'^', urls.include('features.files.urls')),
    urls.url(r'^', urls.include('features.galleries.urls')),
    urls.url(r'^', urls.include('features.stadt.urls')),
    urls.url(r'^', urls.include('features.tags.urls')),

    # matches /*/, should be included late, groups before gestalten
    urls.url(r'^', urls.include('features.groups.urls')),
    urls.url(r'^', urls.include('features.gestalten.urls')),

    # matches /*/*/, should be included at last
    urls.url(r'^', urls.include('features.content.urls')),
] + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
