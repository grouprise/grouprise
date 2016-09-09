from content import views as content_views
from django.conf import settings, urls
from django.conf.urls import static, url, include
from django.contrib import admin
from entities import views as entities_views


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
else:
    urlpatterns = []

urlpatterns = urlpatterns + [
    urls.url(r'^stadt/', urls.include('account.urls')),
    urls.url(r'^stadt/', urls.include('content.urls')),
    urls.url(r'^stadt/', urls.include('entities.urls')),
    urls.url(r'^stadt/', urls.include('features.associations.urls')),
    urls.url(r'^stadt/', urls.include('features.memberships.urls')),
    urls.url(r'^stadt/', urls.include('features.sharing.urls')),
    urls.url(r'^stadt/', urls.include('features.subscriptions.urls')),
    urls.url(r'^stadt/admin/', admin.site.urls),
    urls.url(r'^stadt/api/', urls.include('api.urls')),
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
