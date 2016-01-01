from django.conf import settings, urls
from django.conf.urls import static, url
from django.contrib import admin
from django.views import generic

from content import views as content_views
from entities import views as entities_views


urlpatterns = [
    # index
    url(r'^$', content_views.ContentListView.as_view(), name='index'),
    # root namespace
    url(r'^admin/', admin.site.urls),
    url(r'^auth/', urls.include('allauth.urls')),
    url(r'^auth/settings/$', generic.TemplateView.as_view(template_name='entities/gestalt_settings.html'), name='gestalt-settings'),
    url(r'^gestalt/(?P<pk>[\w-]+)/$', entities_views.GestaltDetailView.as_view(), name='gestalt-detail'),
    # groups
    url(r'^(?P<slug>[\w-]+)$', entities_views.GroupDetailView.as_view(), name='group-detail'),
    url(r'^(?P<group_slug>[\w-]+)/(?P<slug>[\w-]+)/$', content_views.ContentDetailView.as_view(), name='content-detail'),
] + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
