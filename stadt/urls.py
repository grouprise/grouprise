from django.conf.urls import url
from django.contrib import admin

from entities import views as entities_views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^(?P<slug>[\w-]+)$', entities_views.GroupDetailView.as_view()),
]
