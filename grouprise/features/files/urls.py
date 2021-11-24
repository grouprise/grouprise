from django.conf.urls import url
from django.urls import path
from django_downloadview import ObjectDownloadView

from . import views
from .models import File

urlpatterns = [
    url(
        r"^(?P<entity_slug>[\w.@+-]+)/files/add/$",
        views.Create.as_view(),
        name="create-group-file",
    ),
    path(
        "stadt/files/<int:pk>/",
        ObjectDownloadView.as_view(model=File),
        name="download-file",
    ),
]
