from django.urls import path

from .views import ImageDownloadView

urlpatterns = [
    path(
        "-/images/<str:name>",
        ImageDownloadView.as_view(),
        name="download-image",
    ),
]
