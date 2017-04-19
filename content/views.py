from . import creation, forms, models
from django import shortcuts
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.utils import formats
from django.views import generic
from django.views.generic import dates
from django.db.models import Q
from django_ical.views import ICalFeed

import content.models
from core.views.base import GestaltAuthenticationMixin
from entities import models as entities_models
from utils import views as utils_views


class BaseContentList(utils_views.List):
    context_object_name = 'content_list'
    permission = 'content.view_content_list'


class GalleryList(BaseContentList):
    menu = 'gallery'
    title = 'Galerien'

    def get_queryset(self):
        return models.Gallery.objects.permitted(self.request.user)


class Content(utils_views.PageMixin, generic.DetailView):
    inline_view = (creation.CommentCreate, 'comment_form')
    model = models.Content
    permission = 'content.view_content'

    def get_inline_view_kwargs(self):
        return {'content_pk': self.object.pk}

    def get_menu(self):
        return self.object.get_type_name()

    def get_parent(self):
        return self.get_group() or self.object.author

    def get_title(self):
        return self.object.title


class ContentList(BaseContentList):
    def get_queryset(self):
        return models.Content.objects.permitted(self.request.user).filter(
                ~Q(article__isnull=False, public=False))


class ContentUpdate(utils_views.ActionMixin, generic.UpdateView):
    action = 'Beitrag ändern'
    form_class = forms.ContentUpdate
    model = models.Content
    permission = 'content.change_content'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        try:
            kwargs['author'] = self.request.user.gestalt
            kwargs['groupcontent'] = entities_models.GroupContent.objects.get(
                    content=self.object, group=self.get_group())
        finally:
            return kwargs

    def get_menu(self):
        return self.object.get_type_name()

    def get_parent(self):
        return self.object


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


class EventUpdate(utils_views.ActionMixin, generic.UpdateView):
    action = 'Ereignis ändern'
    form_class = forms.Event
    menu = 'event'
    model = models.Event
    permission = 'content.change_content'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['author'] = self.request.user.gestalt
        return kwargs

    def get_initial(self):
        group = self.get_group()
        if group:
            return {
                    'group': group.pk,
                    'pinned': entities_models.GroupContent.objects.get(
                        group=group, content=self.object).pinned
                    }
        else:
            return {}

    def get_parent(self):
        return self.object


class ImageList(utils_views.List):
    permission = 'content.view_image_list'

    def get_breadcrumb_object(self):
        return self.get_content()

    def get_content(self):
        return shortcuts.get_object_or_404(
                models.Content, pk=self.request.resolver_match.kwargs['content_pk'])

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


class BaseCalendarFeed(ICalFeed, GestaltAuthenticationMixin):

    def __call__(self, request, *args, **kwargs):
        self.request = request
        self.kwargs = kwargs
        try:
            return super().__call__(request, *args, **kwargs)
        except PermissionDenied:
            response = HttpResponse()
            response.status_code = 401
            response['WWW-Authenticate'] = 'Basic realm="{}"'.format("stadtgestalten.org")
            return response

    def get_queryset(self):
        user = self.get_authorized_user()
        filter_dict = {}
        self.assemble_content_filter_dict(filter_dict)
        if user is None:
            if filter_dict['public']:
                return content.models.Event.objects.filter(**filter_dict)
            else:
                # non-public items cannot be accessed without being authorized
                raise PermissionDenied
        else:
            return content.models.Event.objects.permitted(user).filter(**filter_dict)

    def assemble_content_filter_dict(self, filter_dict):
        filter_dict['public'] = (self.kwargs['domain'] == 'public')

    def get_authorized_user(self):
        authenticated_gestalt = self.get_authenticated_gestalt(self.get_calendar_owner())
        if authenticated_gestalt:
            if self.check_authorization(authenticated_gestalt):
                return authenticated_gestalt.user
        return None

    def items(self):
        return self.get_queryset().order_by('-time')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.text

    def item_location(self, item):
        return item.place

    def item_start_datetime(self, item):
        return item.time
