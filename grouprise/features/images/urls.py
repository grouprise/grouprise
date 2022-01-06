from django.urls import path

from .views import ImageDownloadView

urlpatterns = [
    path(
        "stadt/images/<int:pk>/",
        ImageDownloadView.as_view(),
        name="download-image",
    ),
]
