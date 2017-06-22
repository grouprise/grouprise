import django
from django.db.models import Q

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
        self.tagged_only = int(self.request.GET.get('tagged', 0))
        tagged_query = Q(content__taggeds__tag=self.tag)
        qs = super().get_queryset().ordered_user_content(self.request.user)
        if self.tagged_only:
            qs = qs.filter(tagged_query)
        else:
            group_tagged_query = (
                    Q(entity_type=groups.Group.content_type)
                    & Q(entity_id__in=self.groups))
            qs = qs.filter(tagged_query | group_tagged_query)
        return qs

    def get_tag(self):
        try:
            return django.shortcuts.get_object_or_404(models.Tag, slug=self.kwargs.get('slug'))
        except django.http.Http404:
            slug = self.kwargs.get(self.slug_url_kwarg)
            return models.Tag(name=slug, slug=slug)
