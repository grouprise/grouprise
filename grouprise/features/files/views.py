from django.shortcuts import get_object_or_404
from django_downloadview import ObjectDownloadView

import grouprise.features.content.views

from . import forms
from .models import File
from ...core.views import PermissionMixin


class Create(grouprise.features.content.views.Create):
    template_name = "files/create.html"

    form_class = forms.Create


class FileDownloadView(PermissionMixin, ObjectDownloadView):
    permission_required = "files.download"

    def get_basename(self):
        return self.object.display_name

    def get_object(self, queryset=None):
        try:
            return get_object_or_404(File, file=self.kwargs["name"])
        except File.MultipleObjectsReturned:
            # TODO: remove this workaround, when #773 is fixed
            return File.objects.filter(file=self.kwargs["name"]).first()
