from content import views as content_views
from django.conf import settings, urls
from django.conf.urls import static
from django.contrib import admin
from entities import views as entities_views

urlpatterns = [
    urls.url(r'^stadt/admin/', admin.site.urls),
    urls.url(r'^stadt/api/', urls.include('core.api_urls')),
    
    urls.url(r'^stadt/', urls.include('account.urls')),
    urls.url(r'^stadt/', urls.include('content.urls')),
    urls.url(r'^stadt/', urls.include('entities.urls')),
    urls.url(r'^stadt/', urls.include('features.articles.urls')),
    urls.url(r'^stadt/', urls.include('features.associations.urls')),
    urls.url(r'^stadt/', urls.include('features.conversations.urls')),
    urls.url(r'^stadt/', urls.include('features.events.urls')),
    urls.url(r'^stadt/', urls.include('features.memberships.urls')),
    urls.url(r'^stadt/', urls.include('features.sharing.urls')),
    urls.url(r'^stadt/', urls.include('features.subscriptions.urls')),
    urls.url(r'^stadt/', urls.include('features.tags.urls')),
    
    urls.url(r'^', urls.include('features.groups.urls')),
    urls.url(r'^', urls.include('features.gestalten.urls')),
    urls.url(r'^', urls.include('features.content.urls')),
    urls.url(r'^', urls.include('features.stadt.urls')),
] + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
