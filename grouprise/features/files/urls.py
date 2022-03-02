from django.conf.urls import url
from django.urls import path

from grouprise.core.utils import get_accelerated_download_view
from . import views
from .views import FileDownloadView


urlpatterns = [
    url(
        r"^(?P<entity_slug>[\w.@+-]+)/files/add/$",
        views.Create.as_view(),
        name="create-group-file",
    ),
    path(
        "-/files/<str:name>",
        get_accelerated_download_view(FileDownloadView.as_view(), "/-/files/"),
        name="download-file",
    ),
]
