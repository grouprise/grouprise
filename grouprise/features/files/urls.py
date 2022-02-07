from django.conf.urls import url
from django.urls import path

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
        FileDownloadView.as_view(),
        name="download-file",
    ),
]
