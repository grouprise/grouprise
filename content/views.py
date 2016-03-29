from . import models
from django import http
from django.conf import settings
from django.contrib import messages
from django.db import models as django_models
from django.forms import models as model_forms
from django.utils import formats
from django.views import generic
from django.views.generic import dates
from entities import models as entities_models
from rules.contrib import views as rules_views
from util import forms as util_forms, views as util_views

class CommentCreate(util_views.ActionMixin, generic.CreateView):
    action = 'Kommentar hinzufügen'
    fields = ('text',)
    layout = 'text'
    model = models.Comment
    permission = 'content.create_comment'

    def form_valid(self, form):
        form.instance.author = self.request.user.gestalt
        form.instance.content = self.get_permission_object()
        return super().form_valid(form)

    def get_menu(self):
        return self.get_parent().get_type_name()

    def get_parent(self):
        pk = self.request.resolver_match.kwargs['content_pk']
        return models.Content.objects.get(pk=pk)

    def get_permission_object(self):
        return self.get_parent()

class Content(util_views.PageMixin, generic.DetailView):
    model = models.Content
    permission = 'content.view_content'
    
    def get_menu(self):
        return self.object.get_type_name()

    def get_parent(self):
        return self.get_group() or self.object.author

    def get_title(self):
        return self.object.title

class ContentCreate(util_views.ActionMixin, generic.CreateView):
    action = 'Beitrag erstellen'

    def form_valid(self, form):
        form.instance.author = self.request.user.gestalt
        self.object = form.save()
        if self.get_group():
            entities_models.GroupContent(content=self.object, group=self.get_group()).save()
        if not form.instance.public:
            messages.success(self.request, 'Deine Nachricht wurde gespeichert.')
        return http.HttpResponseRedirect(self.get_success_url())
    
    def get_permissions(self):
        return {
                'entities.create_group_content': self.get_group(),
                'entities.create_group_message': self.get_group(),
                'entities.create_gestalt_content': self.request.user.gestalt,
                }

    def get_fields(self):
        fields = ['text', 'title']
        if self.has_permission('entities.create_group_content'):
            fields += ['public']
        if self.get_queryset().model == models.Event:
            fields += ['place', 'time']
        return fields

    def get_form_class(self):
        return model_forms.modelform_factory(self.get_queryset().model, fields=self.get_fields())

    def get_layout(self):
        public_layout = ('public',) if self.has_permission('entitites.create_group_content') else tuple()
        event_layout = ('time', 'place') if self.get_queryset().model == models.Event else tuple()
        layout = ('title',) + event_layout + ('text',) + public_layout
        return layout + super().get_layout()

    def get_menu(self):
        return self.get_type_name()

    def get_parent(self):
        return self.get_group() or self.request.user.gestalt

    def get_queryset(self):
        return getattr(models, self.get_type_name())._default_manager.all()

    def get_success_url(self):
        if self.object and not self.object.public:
            return self.get_back_url()
        return super().get_success_url()

    def get_type_name(self):
        return self.request.resolver_match.kwargs['type'].title()

class ContentList(util_views.PageMixin, generic.ListView):
    permission = 'content.view_content_list'

    def get_queryset(self):
        return models.Content.objects.permitted(self.request.user)

class ContentUpdate(util_views.ActionMixin, generic.UpdateView):
    action = 'Beitrag ändern'
    fields = ('text', 'title')
    layout = ('title', 'text')
    model = models.Content
    permission = 'content.change_content'

    def get_menu(self):
        return self.object.get_type_name()

class EventDay(util_views.PageMixin, generic.DayArchiveView):
    allow_future = True
    context_object_name = 'content_list'
    date_field = 'time'
    menu = 'event'
    model = models.Event
    ordering = 'time'
    parent = 'event-index'
    permission = 'content.view_event_day'

    def get_date(self):
        return dates._date_from_string(
                self.get_year(), self.get_year_format(),
                self.get_month(), self.get_month_format(),
                self.get_day(), self.get_day_format())

    def get_title(self):
        return formats.date_format(self.get_date())
