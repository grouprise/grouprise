from django.conf.urls import url
from django.urls import path

from grouprise.core.settings import CORE_SETTINGS
from . import views
from .views import FileDownloadView


def get_accelerated_download_view(view):
    wrapper = CORE_SETTINGS.FILE_DOWNLOAD_WRAPPER
    if wrapper is None:
        return view
    else:
        return wrapper(
            view,
            source_url="/-/files/",
            destination_url="/protected-downloads/",
        )


urlpatterns = [
    url(
        r"^(?P<entity_slug>[\w.@+-]+)/files/add/$",
        views.Create.as_view(),
        name="create-group-file",
    ),
    path(
        "-/files/<str:name>",
        get_accelerated_download_view(FileDownloadView.as_view()),
        name="download-file",
    ),
]
