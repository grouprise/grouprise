from django.conf import settings
from django.conf.urls import static, url
from django.contrib import admin

from content import views as content_views
from entities import views as entities_views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^gestalt/(?P<pk>[\w-]+)/$', entities_views.GestaltDetailView.as_view(), name='gestalt-detail'),
    url(r'^(?P<slug>[\w-]+)$', entities_views.GroupDetailView.as_view(), name='group-detail'),
    url(r'^(?P<group_slug>[\w-]+)/(?P<slug>[\w-]+)/$', content_views.ContentDetailView.as_view(), name='content-detail'),
] + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
