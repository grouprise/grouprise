from content import views as content_views
from django.conf import settings, urls
from django.conf.urls import static
from django.contrib import admin
from django.views import generic
from entities import views as entities_views


urlpatterns = [
    urls.url(r'^stadt/', urls.include('allauth.urls')),
    urls.url(r'^stadt/', urls.include('content.urls')),
    urls.url(r'^stadt/', urls.include('entities.urls')),
    urls.url(r'^stadt/admin/', admin.site.urls),
    urls.url(r'^stadt/imprint/$', generic.TemplateView.as_view(template_name='imprint.html'), name='imprint'),
    urls.url(r'^$', content_views.ContentList.as_view(), name='index'),
    urls.url(r'^gestalt/(?P<slug>[\w.@+-]+)/$', entities_views.Gestalt.as_view(), name='gestalt'),
    urls.url(r'^gestalt/(?P<gestalt_slug>[\w.@+-]+)/(?P<slug>[\w-]+)/$', content_views.Content.as_view(), name='content'),
    urls.url(r'^(?P<slug>[\w-]+)$', entities_views.Group.as_view(), name='group'),
    urls.url(r'^(?P<group_slug>[\w-]+)/(?P<slug>[\w-]+)/$', content_views.Content.as_view(), name='group-content'),
] + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
