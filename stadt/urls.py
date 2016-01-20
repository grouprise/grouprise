from django.conf import settings, urls
from django.conf.urls import static, url
from django.contrib import admin
from django.views import generic

from content import views as content_views
from entities import views as entities_views


urlpatterns = [
    # index
    url(r'^$', content_views.ContentList.as_view(), name='index'),
    # stadt namespace
    url(r'^stadt/', urls.include('allauth.urls')),
    url(r'^stadt/admin/', admin.site.urls),
    url(r'^stadt/content/(?P<pk>[0-9]+)/edit/(?:group=(?P<group_slug>[\w-]+))?$', content_views.ContentUpdate.as_view(), name='content-update'),
    url(r'^stadt/gestalt/settings/$', entities_views.GestaltSettings.as_view(), name='gestalt-settings'),
    url(r'^stadt/group/(?P<pk>[0-9]+)/edit/$', entities_views.GroupUpdate.as_view(), name='group-update'),
    url(r'^stadt/imprint/$', generic.TemplateView.as_view(template_name='imprint.html'), name='imprint'),
    # gestalt namespaces
    url(r'^gestalt/(?P<slug>[\w-]+)/$', entities_views.Gestalt.as_view(), name='gestalt'),
    url(r'^gestalt/(?P<gestalt_slug>[\w-]+)/(?P<slug>[\w-]+)/$', content_views.ContentDetail.as_view(), name='content'),
    # group namespaces
    url(r'^(?P<slug>[\w-]+)$', entities_views.GroupDetail.as_view(), name='group'),
    url(r'^(?P<group_slug>[\w-]+)/(?P<slug>[\w-]+)/$', content_views.ContentDetail.as_view(), name='group-content'),
] + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
