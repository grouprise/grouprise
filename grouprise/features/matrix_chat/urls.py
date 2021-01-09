from django.conf import settings
from django.urls import include, path


if "grouprise.features.matrix_chat" in settings.INSTALLED_APPS:
    urlpatterns = [
        path("cas/", include("cas_server.urls", namespace="cas_server")),
    ]
else:
    urlpatterns = []
