from django.urls import path

from grouprise.core.utils import get_accelerated_download_view
from .views import ImageDownloadView

urlpatterns = [
    path(
        "-/images/<str:name>",
        get_accelerated_download_view(ImageDownloadView.as_view(), "/-/images/"),
        name="download-image",
    ),
]
