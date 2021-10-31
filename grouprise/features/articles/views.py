from django.views import generic

import grouprise.features.content.views
from grouprise.core.views import PermissionMixin
from grouprise.features.associations import models as associations
from . import forms


class List(PermissionMixin, generic.ListView):
    permission_required = "articles.view_list"
    model = associations.Association
    template_name = "articles/list.html"
    paginate_by = 10

    def get_content(self):
        return associations.Association.objects.can_view(self.request.user)

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .ordered_user_content(self.request.user)
            .filter_articles()
        )


class Create(grouprise.features.content.views.Create):
    form_class = forms.Create
    template_name = "articles/create.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["with_time"] = False
        return kwargs
