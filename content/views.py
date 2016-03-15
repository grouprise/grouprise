from . import models
from crispy_forms import bootstrap, layout
from django import http
from django.contrib import messages
from django.db import models as django_models
from django.forms import models as model_forms
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
    model = models.Article
    template_name = 'content/content_form.html'

    def form_valid(self, form):
        self.group = self.get_group()
        form.instance.author = self.request.user.gestalt
        self.object = form.save()
        if self.group:
            entities_models.GroupContent(content=self.object, group=self.group).save()
        if not form.instance.public:
            messages.success(self.request, 'Deine Nachricht wurde gespeichert.')
        return http.HttpResponseRedirect(self.get_success_url())
    
    def get_any_permission_required(self):
        return {
                'internal_and_public': [
                    ('entities.create_group_content', self.get_group()),
                    ],
                'only_internal': [
                    ('entities.create_group_message', self.get_group()),
                    ],
                'only_public': [
                    ('entities.create_gestalt_content', self.request.user.gestalt),
                    ],
                }

    def get_back_url(self):
        try:
            return self.group.get_absolute_url()
        except AttributeError:
            return self.request.user.gestalt.get_absolute_url()

    def get_fields(self):
        fields = ['text', 'title']
        if self.has_permission('internal_and_public'):
            fields += ['public']
        return fields

    def get_form_class(self):
        return model_forms.modelform_factory(self.model, fields=self.get_fields())

    def get_layout(self):
        public_list = ['public'] if self.has_permission('internal_and_public') else []
        layout_list = ['title', 'text'] + public_list + [
                bootstrap.FormActions(layout.Submit('submit', 'Beitrag speichern / Nachricht senden')),
                ]
        return layout_list

    def get_success_url(self):
        if not self.object.public:
            return self.get_back_url()
        return super().get_success_url()

    def has_permission(self, permissions=None):
        perms = []
        if not permissions:
            for ps in self.get_any_permission_required().values():
                perms += ps
        else:
            perms = self.get_any_permission_required()[permissions]
        for perm in perms:
            if self.request.user.has_perm(perm[0], perm[1]):
                return True
        return False


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
