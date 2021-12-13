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
    model = File
