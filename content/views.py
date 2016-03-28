from . import models
from django import http
from django.contrib import messages
from django.db import models as django_models
from django.forms import models as model_forms
from django.views import generic
from entities import models as entities_models
from rules.contrib import views as rules_views
from util import forms as util_forms, views as util_views


class CommentCreate(
        rules_views.PermissionRequiredMixin,
        util_views.FormMixin, 
        generic.CreateView):
    fields = ['text']
    layout = ['text', util_forms.Submit('Kommentar / Antwort speichern / senden')]
    model = models.Comment
    permission_required = 'content.create_comment'

    def form_valid(self, form):
        form.instance.author = self.request.user.gestalt
        form.instance.content = self.get_permission_object()
        return super().form_valid(form)

    def get_permission_object(self):
        pk = self.request.resolver_match.kwargs['content_pk']
        return models.Content.objects.get(pk=pk)

    def get_success_url(self):
        return self.get_permission_object().get_absolute_url()


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
        util_views.FormMixin, 
        util_views.NavigationMixin,
        generic.CreateView):
    DECIDE_ON_PUBLICATION = 'both'
    PUBLISH_ONLY_INTERNALLY = 'intern'
    PUBLISH_ONLY_PUBLICALLY = 'public'

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
                self.DECIDE_ON_PUBLICATION: [
                    ('entities.create_group_content', self.get_group()),
                    ],
                self.PUBLISH_ONLY_INTERNALLY: [
                    ('entities.create_group_message', self.get_group()),
                    ],
                self.PUBLISH_ONLY_PUBLICALLY: [
                    ('entities.create_gestalt_content', self.request.user.gestalt),
                    ],
                }

    def get_back_url(self):
        try:
            return self.get_group().get_absolute_url()
        except AttributeError:
            return self.request.user.gestalt.get_absolute_url()

    def get_fields(self):
        fields = ['text', 'title']
        if self.has_permission(self.DECIDE_ON_PUBLICATION):
            fields += ['public']
        if self.get_queryset().model == models.Event:
            fields += ['place', 'time']
        return fields

    def get_form_class(self):
        return model_forms.modelform_factory(self.get_queryset().model, fields=self.get_fields())

    def get_layout(self):
        public_list = ['public'] if self.has_permission(self.DECIDE_ON_PUBLICATION) else []
        event_list = ['time', 'place'] if self.get_queryset().model == models.Event else []
        layout_list = ['title'] + event_list + ['text'] + public_list + [util_views.submit('Beitrag speichern / Nachricht senden')]
        return layout_list

    def get_queryset(self):
        try:
            content_type = self.request.resolver_match.kwargs['type']
        except KeyError:
            content_type = 'article'
        return getattr(models, content_type.title())._default_manager.all()

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


class ContentList(util_views.PageMixin, generic.ListView):
    permission = 'content.view_content_list'

    def get_queryset(self):
        return models.Content.objects.permitted(self.request.user)


class ContentUpdate(
        rules_views.PermissionRequiredMixin, 
        util_views.FormMixin, 
        util_views.NavigationMixin,
        generic.UpdateView):
    fields = ['text', 'title']
    layout = ['title', 'text', util_forms.Submit('Beitrag speichern')]
    model = models.Content
    permission_required = 'content.change_content'


class EventDay(generic.DayArchiveView):
    allow_future = True
    date_field = 'time'
    model = models.Event
    ordering = 'time'
    template_name_suffix = '_day'
