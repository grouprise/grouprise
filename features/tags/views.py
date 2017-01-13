from . import models
from core.views import base
from django.contrib.contenttypes import models as contenttypes
from django.views import generic
from features.groups import models as groups


class Tag(base.PermissionMixin, generic.DetailView):
    permission_required = 'tags.view'
    model = models.Tag
    template_name = 'tags/tag.html'

    def get_group_tags(self):
        return models.Tag.objects.filter(
                name=self.object.name,
                tagged_type=contenttypes.ContentType.objects.get_for_model(groups.Group))
