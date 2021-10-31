from django.contrib import admin
from django.conf.urls import url
from django.urls import path

from grouprise.core.views import LogoRedirects, Markdown


urlpatterns = [
    path("stadt/admin/", admin.site.urls),
    path("stadt/markdown/", Markdown.as_view(), name="markdown"),
    url(r"stadt/logos/(?P<name>\w+)", LogoRedirects.as_view(), name="logos"),
]
