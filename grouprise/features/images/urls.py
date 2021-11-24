from django.urls import path
from django_downloadview import ObjectDownloadView

from .models import Image

urlpatterns = [
    path(
        "stadt/images/<int:pk>/",
        ObjectDownloadView.as_view(model=Image),
        name="download-image",
    ),
]
