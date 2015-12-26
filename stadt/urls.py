from django.conf import settings
from django.conf.urls import static, url
from django.contrib import admin

from entities import views as entities_views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^(?P<slug>[\w-]+)$', entities_views.GroupDetailView.as_view()),
] + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
