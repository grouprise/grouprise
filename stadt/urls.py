from content import views as content_views
from django.conf import settings, urls
from django.conf.urls import static
from django.contrib import admin
from entities import views as entities_views

urlpatterns = [
    urls.url(r'^stadt/', urls.include('account.urls')),
    urls.url(r'^stadt/', urls.include('content.urls')),
    urls.url(r'^stadt/', urls.include('entities.urls')),
    urls.url(r'^stadt/', urls.include('features.articles.urls')),
    urls.url(r'^stadt/', urls.include('features.associations.urls')),
    urls.url(r'^stadt/', urls.include('features.conversations.urls')),
    urls.url(r'^stadt/', urls.include('features.events.urls')),
    urls.url(r'^stadt/', urls.include('features.gestalten.urls')),
    urls.url(r'^stadt/', urls.include('features.groups.urls')),
    urls.url(r'^stadt/', urls.include('features.memberships.urls')),
    urls.url(r'^stadt/', urls.include('features.sharing.urls')),
    urls.url(r'^stadt/', urls.include('features.subscriptions.urls')),
    urls.url(r'^stadt/', urls.include('features.tags.urls')),
    urls.url(r'^stadt/api/', urls.include('core.api_urls')),
    urls.url(r'^stadt/admin/', admin.site.urls),
    urls.url(r'^$', content_views.ContentList.as_view(), name='index'),

    urls.url(
        r'^gestalt/(?P<gestalt_slug>[\w.@+-]+)/$',
        entities_views.Gestalt.as_view(),
        name='gestalt'),

    urls.url(
        r'^gestalt/(?P<gestalt_slug>[\w.@+-]+)/(?P<slug>[\w-]+)/$',
        content_views.Content.as_view(),
        name='gestalt-content'),

    urls.url(
        r'^(?P<group_slug>[\w-]+)/$',
        entities_views.Group.as_view(),
        name='group'),

    urls.url(
        r'^(?P<group_slug>[\w-]+)/(?P<slug>[\w-]+)/$',
        content_views.Content.as_view(),
        name='content'),

] + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
