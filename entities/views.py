from . import filters, forms, models
from content import creation as content_creation, models as content_models
from crispy_forms import bootstrap, layout
from django import http, shortcuts
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import mixins as auth_mixins
from django.contrib.sites import models as sites_models
from django.core import urlresolvers
from django.db import models as django_models
from django.utils import six
from django.views import generic
from django_filters import views as filters_views
from rules.contrib import views as rules_views
from utils import forms as utils_forms, views as utils_views


class Gestalt(utils_views.List):
    menu = 'gestalt'
    permission = 'entities.view_gestalt'
    sidebar = ('calendar',)
    template_name = 'entities/gestalt_detail.html'

    def get_permission_object(self):
        return self.get_gestalt()

    def get_queryset(self):
        return content_models.Content.objects.permitted(self.request.user).filter(django_models.Q(gestaltcontent__gestalt=self.get_gestalt()) | django_models.Q(author=self.get_gestalt()))

    def get_title(self):
        return str(self.get_gestalt())

class GestaltList(utils_views.List):
    menu = 'gestalt'
    permission = 'content.view_content_list'
    queryset = models.Gestalt.objects.filter(public=True)
    title = 'Gestalten'

class GestaltUpdate(utils_views.ActionMixin, generic.UpdateView):
    action = 'Dein Profil'
    form_class = forms.Gestalt
    menu = 'gestalt'
    message = 'Die Einstellungen wurden geändert.'
    model = models.Gestalt
    permission = 'entities.change_gestalt'

    def get_parent(self):
        return self.object


class GestaltAvatarUpdate(utils_views.ActionMixin, generic.UpdateView):
    action = 'Avatar ändern'
    fields = ('avatar',)
    layout = ('avatar',)
    menu = 'gestalt'
    model = models.Gestalt
    permission = 'entities.change_gestalt'

    def get_parent(self):
        return self.object


class GestaltBackgroundUpdate(utils_views.ActionMixin, generic.UpdateView):
    action = 'Hintergrundbild ändern'
    fields = ('background',)
    layout = ('background',)
    menu = 'gestalt'
    model = models.Gestalt
    permission = 'entities.change_gestalt'

    def get_parent(self):
        return self.object


class Group(utils_views.List):
    inline_view = (content_creation.Gallery, 'intro_gallery_form')
    menu = 'group'
    permission = 'entities.view_group'
    template_name = 'entities/group_detail.html'

    def get(self, *args, **kwargs):
        if not self.get_group():
            raise http.Http404('Gruppe nicht gefunden')
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['calendar_events'] = self.get_events().around()
        kwargs['intro_content'] = self.get_intro_content()
        kwargs['internal_messages'] = self.get_messages()
        kwargs['sidebar_groups'] = models.Group.objects.exclude(pk=self.get_group().pk).scored().similar(self.get_group()).order_by('-score')
        kwargs['upcoming_events'] = self.get_events().upcoming(3)
        return super().get_context_data(**kwargs)

    def get_events(self):
        return content_models.Event.objects.permitted(self.request.user).filter(groups=self.get_group())

    def get_group_content(self):
        return self.get_group().content.permitted(self.request.user)

    def get_inline_view_form(self):
        # FIXME: hacky code follows
        if (self.request.user.has_perm('entities.create_group_content', self.get_group())
                and not self.get_group().get_head_gallery()):
            form = super().get_inline_view_form()
            form.helper.filter(six.string_types).wrap(layout.Field)
            form.helper.filter(layout.Field).update_attributes(
                    **{'data-component': '', 'type': 'hidden'})
            del form.helper[-1]
            form.helper.layout.append(utils_forms.Submit('<i class="sg sg-2x sg-camera"></i>', 'gallery-create', 'btn btn-backdrop btn-ts'))
            form.initial['image_creation_redirect'] = True
            form.initial['pinned'] = True
            form.initial['public'] = True
            form.initial['text'] = 'Introgalerie der Gruppe @{}'.format(self.get_group().slug)
            form.initial['title'] = self.get_group()
            return form
        return None

    def get_intro_content(self):
        pinned_content = self.get_group_content().filter(groupcontent__pinned=True)
        try:
            return pinned_content.exclude(pk=self.get_group().get_head_gallery().pk)
        except AttributeError:
            return pinned_content

    def get_messages(self):
        return self.get_group_content().filter(groupcontent__pinned=False).filter(article__isnull=False, public=False).order_by('-comments__date_created', '-date_created')[:3]

    def get_queryset(self):
        return self.get_group_content().filter(groupcontent__pinned=False).exclude(article__isnull=False, public=False)

    def get_related_object(self):
        return self.get_group()

    def get_title(self):
        return self.get_group().name


class GroupAvatarUpdate(utils_views.ActionMixin, generic.UpdateView):
    action = 'Avatar ändern'
    fields = ('avatar',)
    layout = ('avatar',)
    menu = 'group'
    model = models.Group
    permission = 'groups.change_group'

    def get_parent(self):
        return self.object


class GroupCreate(utils_views.ActionMixin, generic.CreateView):
    action = 'Gruppe anlegen'
    fields = ('name',)
    layout = 'name'
    menu = 'group'
    model = models.Group
    parent = 'group-index'
    permission = 'entities.create_group'

    def get_initial(self):
        if 'name' in self.request.GET:
            return {'name': self.request.GET['name']}

class GroupList(utils_views.PageMixin, filters_views.FilterView):
    filterset_class = filters.Group
    menu = 'group'
    ordering = '-score'
    permission = 'content.view_content_list'
    sidebar = ('calendar',)
    title = 'Gruppen'

    def get_queryset(self):
        return models.Group.objects.scored()


class GroupLogoUpdate(utils_views.ActionMixin, generic.UpdateView):
    action = 'Logo ändern'
    fields = ('logo',)
    layout = ('logo',)
    menu = 'group'
    model = models.Group
    permission = 'groups.change_group'

    def get_parent(self):
        return self.object


class GroupMessages(utils_views.List):
    menu = 'group'
    permission = 'content.view_content_list'
    sidebar = []
    template_name = 'stadt/list.html'
    title = 'Nachrichten'

    def get_queryset(self):
        return self.get_group().content.permitted(self.request.user).filter(article__isnull=False, public=False).order_by('-comments__date_created', '-date_created')

    def get_parent(self):
        return self.get_group()

    def get_related_object(self):
        return self.get_group()


class GroupUpdate(utils_views.ActionMixin, generic.UpdateView):
    action = 'Gruppe ändern'
    fields = ['address', 'closed', 'description', 'date_founded', 'name', 'slug', 'url']
    menu = 'group'
    model = models.Group
    permission = 'groups.change_group'

    def get_layout(self):
        return (
                'name',
                layout.Field('description', rows=4),
                layout.Field('address', rows=4),
                'url',
                layout.Field('date_founded', data_component='date'),
                bootstrap.PrependedText('slug', '%(domain)s/' % {'domain': sites_models.Site.objects.get_current().domain}),
                'closed',
                ) + super().get_layout()

    def get_parent(self):
        return self.object


class Imprint(utils_views.PageMixin, generic.TemplateView):
    permission = 'entities.view_imprint'
    template_name = 'entities/imprint.html'
    title = 'Impressum'
