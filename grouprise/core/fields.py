from django.db.models import FileField
from django.db.models.fields.files import FieldFile
from django.urls import reverse


class ProtectedFieldFile(FieldFile):
    @property
    def url(self):
        self._require_file()
        return reverse("download-file", args=[self.instance.pk])


class ProtectedFileField(FileField):
    attr_class = ProtectedFieldFile
