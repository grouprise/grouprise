import django.db.models
from django.views import generic

from core.views import base
import features.content.views
from features.associations import models as associations
from features.content import models as content


class List(base.PermissionMixin, generic.ListView):
    permission_required = 'articles.view_list'
    model = associations.Association
    template_name = 'articles/list.html'
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().filter(
                container_type=content.Content.get_content_type(), content__time__isnull=True,
                ).can_view(self.request.user).annotate(time_created=django.db.models.Min(
                'content__versions__time_created')).order_by('-time_created')


class Create(features.content.views.Create):
    template_name = 'articles/create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['with_time'] = False
        return kwargs
