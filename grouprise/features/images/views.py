from django_downloadview import ObjectDownloadView

from .models import Image
from ...core.views import PermissionMixin


class ImageDownloadView(PermissionMixin, ObjectDownloadView):
    permission_required = "images.download"
    model = Image
