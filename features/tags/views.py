from . import models
from content import models as content
from core.views import base
from django.contrib.contenttypes import models as contenttypes
from django.core import paginator
from django.views import generic
from features.groups import models as groups


class Tag(base.PermissionMixin, generic.DetailView):
    permission_required = 'tags.view'
    model = models.Tag
    template_name = 'tags/tag.html'

    def get_events(self):
        return self.get_content().exclude(event=None)

    def get_content(self):
        group_ids = self.get_group_tags().values_list('tagged_id', flat=True)
        return content.Content.objects.filter(groupcontent__group__in=group_ids)

    def get_content_page(self):
        group_ids = models.Tag.objects.filter(
                name=self.object.name,
                tagged_type=contenttypes.ContentType.objects.get_for_model(groups.Group)
                ).values_list('tagged_id', flat=True)
        pagin = paginator.Paginator(self.get_content(), 10)
        try:
            return pagin.page(self.request.GET.get('page'))
        except:
            return pagin.page(1)

    def get_group_tags(self):
        return models.Tag.objects.filter(
                name=self.object.name,
                tagged_type=contenttypes.ContentType.objects.get_for_model(groups.Group))
