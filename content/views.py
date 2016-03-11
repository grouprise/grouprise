from . import models
from crispy_forms import bootstrap, layout
from django.core import urlresolvers
from django.db import models as django_models
from django.views import generic
from entities import models as entities_models
from rules.contrib import views as rules_views
from util import views as util_views


class BackToEntityMixin(util_views.GroupMixin, util_views.NavigationMixin):
    def get_back_url(self):
        entity = self.get_group()
        if not entity:
            if self.object:
                entity = self.object.author
            else:
                entity = self.request.user.gestalt
        return entity.get_absolute_url()
    

class SuccessToContentMixin(util_views.GroupMixin, util_views.NavigationMixin):
    def get_success_url(self):
        try:
            return urlresolvers.reverse('group-content', args=[self.get_group().slug, self.object.slug])
        except entities_models.Group.DoesNotExist:
            return super().get_success_url()


class ContentCreate(
        rules_views.PermissionRequiredMixin, 
        BackToEntityMixin, 
        SuccessToContentMixin, 
        util_views.LayoutMixin, 
        generic.CreateView):
    fields = ['public', 'text', 'title']
    layout = [
            'title',
            'text',
            'public',
            bootstrap.FormActions(layout.Submit('submit', 'Beitrag speichern')),
            ]
    model = models.Article
    template_name = 'content/content_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user.gestalt
        response = super().form_valid(form)
        try:
            entities_models.GroupContent(
                    content=self.object, 
                    group=self.get_group()
                    ).save()
        except entities_models.Group.DoesNotExist:
            pass
        return response

    def has_permission(self):
        try:
            return self.request.user.has_perm('content.create_group_content', self.get_group())
        except entities_models.Group.DoesNotExist:
            return self.request.user.has_perm('content.create_gestalt_content', self.request.user.gestalt)


class ContentDetail(
        rules_views.PermissionRequiredMixin, 
        BackToEntityMixin, 
        generic.DetailView):
    model = models.Content
    permission_required = 'content.view_content'


class ContentList(generic.ListView):
    def get_queryset(self):
        return models.Content.objects.permitted(self.request.user)


class ContentUpdate(
        rules_views.PermissionRequiredMixin, 
        SuccessToContentMixin, 
        util_views.LayoutMixin, 
        generic.UpdateView):
    fields = ['text', 'title']
    layout = [
            'title',
            'text',
            bootstrap.FormActions(layout.Submit('submit', 'Beitrag speichern')),
            ]
    model = models.Content
    permission_required = 'content.change_content'


class EventDay(generic.DayArchiveView):
    allow_future = True
    date_field = 'time'
    model = models.Event
    ordering = 'time'
    template_name_suffix = '_day'
