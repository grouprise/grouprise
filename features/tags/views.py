import django

import core
from features.associations import models as associations
from features.content import models as content
from features.groups import models as groups
from . import models


class Detail(core.views.PermissionMixin, django.views.generic.ListView):
    permission_required = 'tags.view'
    model = associations.Association
    paginate_by = 10
    template_name = 'tags/detail.html'

    def get_queryset(self):
        self.tag = self.get_tag()
        self.groups = groups.Group.objects.filter(tags__tag=self.tag)
        return super().get_queryset().filter(
                container_type=content.Content.content_type,
                entity_type=groups.Group.content_type, entity_id__in=self.groups
                ).can_view(self.request.user).annotate(time_created=django.db.models.Min(
                    'content__versions__time_created')).order_by('-time_created')

    def get_tag(self):
        try:
            return django.shortcuts.get_object_or_404(models.Tag, slug=self.kwargs.get('slug'))
        except django.http.Http404:
            slug = self.kwargs.get(self.slug_url_kwarg)
            return models.Tag(name=slug, slug=slug)
