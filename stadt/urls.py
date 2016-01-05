from django.conf import settings, urls
from django.conf.urls import static, url
from django.contrib import admin
from django.views import generic

from content import views as content_views
from entities import views as entities_views


urlpatterns = [
    # index
    url(r'^$', content_views.ContentListView.as_view(), name='index'),
    # stadt namespace
    url(r'^stadt/', urls.include('allauth.urls')),
    url(r'^stadt/admin/', admin.site.urls),
    url(r'^stadt/group/(?P<pk>[0-9]+)/edit/$', entities_views.GroupUpdate.as_view(), name='group-update'),
    url(r'^stadt/imprint/$', generic.TemplateView.as_view(template_name='imprint.html'), name='imprint'),
    url(r'^stadt/settings/$', generic.TemplateView.as_view(template_name='entities/gestalt_settings.html'), name='gestalt-settings'),
    # gestalt namespaces
    url(r'^gestalt/(?P<pk>[\w-]+)/$', entities_views.GestaltDetail.as_view(), name='gestalt-detail'),
    # group namespaces
    url(r'^(?P<slug>[\w-]+)$', entities_views.GroupDetail.as_view(), name='group-detail'),
    url(r'^(?P<group_slug>[\w-]+)/(?P<slug>[\w-]+)/$', content_views.ContentDetailView.as_view(), name='content-detail'),
] + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
