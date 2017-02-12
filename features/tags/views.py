from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404
from django.views import generic
from core.views import base
from features.groups import models as groups
from content import models as contents
from . import models


class Tag(base.PermissionMixin, generic.DetailView):
    permission_required = 'tags.view'
    model = models.Tag
    template_name = 'tags/tag.html'
    sidebar = ()

    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset)
        except Http404:
            slug = self.kwargs.get(self.slug_url_kwarg)
            tag = models.Tag()
            tag.name = slug
            return tag

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if context['object'].pk is not None:
            context['no_data'] = False
            context['tagged_groups'] = self.get_groups()
            context.update(self.get_content_page())
        else:
            context['no_data'] = True

        return context

    def get_groups(self):
        return models.Tagged.get_tagged_models(self.object, groups.Group)

    def get_content(self):
        return models.Tagged.get_tagged_models(self.object, contents.Content)

    def get_content_page(self):
        context = {}
        paginator = Paginator(self.get_content(), 10)
        context['paginator'] = paginator
        try:
            page = self.request.GET.get('page', 1)
            context['content_page'] = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            context['content_page'] = paginator.page(1)
        return context
