from django.shortcuts import get_object_or_404
from django_downloadview import ObjectDownloadView

from .models import Image
from ...core.views import PermissionMixin


class ImageDownloadView(PermissionMixin, ObjectDownloadView):
    permission_required = "images.download"

    def get_object(self, queryset=None):
        return get_object_or_404(Image, file=self.kwargs["name"])
