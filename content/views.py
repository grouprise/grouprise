from . import models
from crispy_forms import bootstrap, layout
from django.db import models as django_models
from django.views import generic
from entities import models as entities_models
from rules.contrib import views as rules_views
from util import views as util_views


class Content(
        rules_views.PermissionRequiredMixin, 
        util_views.GroupMixin,
        util_views.NavigationMixin,
        generic.DetailView):
    model = models.Content
    permission_required = 'content.view_content'
    
    def get_back_url(self):
        try:
            return self.get_group().get_absolute_url()
        except AttributeError:
            return self.object.author.get_absolute_url()


class ContentCreate(
        rules_views.PermissionRequiredMixin, 
        util_views.GroupMixin,
        util_views.LayoutMixin, 
        util_views.NavigationMixin,
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
        group = self.get_group()
        if group:
            entities_models.GroupContent(content=self.object, group=group).save()
        return response
    
    def get_back_url(self):
        try:
            return self.get_group().get_absolute_url()
        except AttributeError:
            return self.request.user.gestalt.get_absolute_url()

    def has_permission(self):
        return self.request.user.has_perm('entities.create_group_content', self.get_group()) or self.request.user.has_perm('entities.create_gestalt_content', self.request.user.gestalt)


class ContentList(generic.ListView):
    def get_queryset(self):
        return models.Content.objects.permitted(self.request.user)


class ContentUpdate(
        rules_views.PermissionRequiredMixin, 
        util_views.LayoutMixin, 
        util_views.NavigationMixin,
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
