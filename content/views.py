from . import models
from crispy_forms import bootstrap, layout
from django.core import urlresolvers
from django.views import generic
from entities import models as entities_models
from rules.contrib import views as rules_views
from util import views as util_views


class ContentNavigationMixin(util_views.GroupMixin, util_views.NavigationMixin):
    def get_back_url(self):
        try:
            entity = self.get_group()
        except entities_models.Group.DoesNotExist:
            entity = self.object.author
        return entity.get_absolute_url()


class ContentCreate(rules_views.PermissionRequiredMixin, ContentNavigationMixin, generic.CreateView):
    fields = ['text', 'title']
    model = models.Article
    permission_required = 'content.create_group_content'
    template_name = 'content/content_form.html'

    def get_permission_object(self):
        return self.get_group()


class ContentDetail(rules_views.PermissionRequiredMixin, ContentNavigationMixin, generic.DetailView):
    model = models.Content
    permission_required = 'content.view_content'


class ContentList(generic.ListView):
    model = models.Content


class ContentUpdate(rules_views.PermissionRequiredMixin, util_views.NavigationMixin, util_views.GroupMixin, util_views.LayoutMixin, generic.UpdateView):
    fields = ['text', 'title']
    layout = [
            'title',
            'text',
            bootstrap.FormActions(layout.Submit('submit', 'Beitrag speichern')),
            ]
    model = models.Content
    permission_required = 'content.change_content'
    
    def get_success_url(self):
        try:
            return urlresolvers.reverse('group-content', args=[self.get_group().slug, self.object.slug])
        except entities_models.Group.DoesNotExist:
            return super().get_success_url()
