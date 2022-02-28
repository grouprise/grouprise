from typing import Callable

from django.db import models
from django.db.models.fields import files
from django.db.models.fields.files import FieldFile
from django.urls import NoReverseMatch, reverse

from grouprise.core.storage import Storage


class DownloadFieldFileMixin:
    download_view_name: str
    instance: models.Model
    _require_file: Callable

    @property
    def url(self):
        self._require_file()
        try:
            return reverse(self.download_view_name, args=[self.name])
        except NoReverseMatch:
            return f"/-/files/{self.name}"


class DownloadFieldFile(DownloadFieldFileMixin, FieldFile):
    download_view_name = "download-file"


class DownloadFileField(models.FileField):
    attr_class = DownloadFieldFile

    def __init__(self, *args, **kwargs):
        if "storage" not in kwargs:
            kwargs["storage"] = Storage()
        super().__init__(*args, **kwargs)


class DownloadImageFieldFile(DownloadFieldFileMixin, files.ImageFieldFile):
    download_view_name = "download-image"


class DownloadImageField(models.ImageField):
    attr_class = DownloadImageFieldFile

    def __init__(self, *args, **kwargs):
        if "storage" not in kwargs:
            kwargs["storage"] = Storage()
        super().__init__(*args, **kwargs)
