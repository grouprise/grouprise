from . import creation, forms, models
from django import http, shortcuts
from django.forms import models as model_forms
from django.utils import formats
from django.views import generic
from django.views.generic import dates
from entities import models as entities_models
from utils import forms as utils_forms, views as utils_views

class BaseContentList(utils_views.List):
    context_object_name = 'content_list'
    parent = 'index'
    permission = 'content.view_content_list'

class ArticleList(BaseContentList):
    menu = 'article'
    title = 'Artikel'

    def get_queryset(self):
        return models.Article.objects.permitted(self.request.user)

class EventList(BaseContentList):
    menu = 'event'
    sidebar = ('groups',)
    title = 'Ereignisse'

    def get_queryset(self):
        return models.Event.objects.permitted(self.request.user).upcoming()

class GalleryList(BaseContentList):
    menu = 'gallery'
    title = 'Galerien'

    def get_queryset(self):
        return models.Gallery.objects.permitted(self.request.user)


class Content(utils_views.PageMixin, generic.DetailView):
    model = models.Content
    permission = 'content.view_content'

    def get_context_data(self, **kwargs):
        v = creation.CommentCreate()
        v.request = self.request
        v.args = self.args
        v.kwargs = self.kwargs
        v.kwargs['content_pk'] = self.object.pk
        kwargs['comment_form'] = v.get_form()
        return super().get_context_data(**kwargs)
    
    def get_menu(self):
        return self.object.get_type_name()

    def get_parent(self):
        return self.get_group() or self.object.author

    def get_title(self):
        return self.object.title


class ContentList(BaseContentList):
    parent = None

    def get_queryset(self):
        return models.Content.objects.permitted(self.request.user)

class ContentUpdate(utils_views.ActionMixin, generic.UpdateView):
    action = 'Beitrag ändern'
    form_class = forms.ContentUpdate
    model = models.Content
    permission = 'content.change_content'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        try:
            kwargs['groupcontent'] = entities_models.GroupContent.objects.get(content=self.object, group=self.get_group())
        finally:
            return kwargs

    def get_menu(self):
        return self.object.get_type_name()

class EventDay(utils_views.PageMixin, generic.DayArchiveView):
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

    def get_queryset(self):
        if self.get_group():
            return super().get_queryset().filter(groups=self.get_group())
        else:
            return super().get_queryset()

    def get_title(self):
        return formats.date_format(self.get_date())


class ImageList(utils_views.List):
    permission = 'content.view_image_list'

    def get_content(self):
        return shortcuts.get_object_or_404(models.Content, pk=self.request.resolver_match.kwargs['content_pk'])

    def get_context_data(self, **kwargs):
        kwargs['content'] = self.get_content()
        return super().get_context_data(**kwargs)

    def get_menu(self):
        return self.get_content().get_type_name()

    def get_permission_object(self):
        return self.get_content()

    def get_queryset(self):
        return models.Image.objects.filter(content=self.get_content())

    def get_title(self):
        return self.get_content().title


class Markdown(utils_views.PageMixin, generic.TemplateView):
    permission = 'content.view_help'
    sidebar = tuple()
    template_name = 'content/markdown.html'
    title = 'Textauszeichnung'
