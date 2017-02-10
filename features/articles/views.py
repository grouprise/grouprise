from content import models
from core.views import base
from django.views import generic


class List(base.PermissionMixin, generic.ListView):
    permission_required = 'articles.view_list'
    template_name = 'articles/list.html'
    paginate_by = 10

    def get_queryset(self):
        return models.Article.objects.can_view(self.request.user)
