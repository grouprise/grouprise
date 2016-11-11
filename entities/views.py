from . import forms, models
from content import creation as content_creation, models as content_models
from crispy_forms import bootstrap, layout
from django import http
from django.contrib.sites import models as sites_models
from django.db import models as django_models
from django.utils import six
from django.views import generic
from features.groups import models as groups
from utils import forms as utils_forms, views as utils_views


class Gestalt(utils_views.List):
    menu = 'gestalt'
    permission = 'entities.view_gestalt'
    sidebar = ('calendar',)
    template_name = 'entities/gestalt_detail.html'

    def get(self, request, *args, **kwargs):
        if not self.get_gestalt():
            raise http.Http404('Gestalt nicht gefunden')
        return super().get(request, *args, **kwargs)

    def get_permission_object(self):
        return self.get_gestalt()

    def get_queryset(self):
        return content_models.Content.objects.permitted(self.request.user).filter(
                django_models.Q(gestaltcontent__gestalt=self.get_gestalt())
                | django_models.Q(author=self.get_gestalt()))

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
        kwargs['upcoming_events'] = self.get_events().upcoming(3)
        return super().get_context_data(**kwargs)

    def get_events(self):
        return content_models.Event.objects.permitted(self.request.user).filter(
                groups=self.get_group())

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
            for i, item in enumerate(form.helper.layout):
                if type(item) == utils_forms.Submit:
                    form.helper.layout.pop(i)
                    break
            form.helper.layout.append(utils_forms.Submit(
                '<i class="sg sg-2x sg-camera"></i>', 'gallery-create', 'btn btn-backdrop btn-ts'))
            form.initial['pinned'] = True
            form.initial['public'] = True
            form.initial['text'] = 'Introgalerie der Gruppe @{}'.format(self.get_group().slug)
            form.initial['title'] = self.get_group()
            return form
        return None

    def get_intro_content(self):
        pinned_content = self.get_group_content().filter(
                groupcontent__pinned=True).order_by('date_created')
        try:
            return pinned_content.exclude(pk=self.get_group().get_head_gallery().pk)
        except AttributeError:
            return pinned_content

    def get_queryset(self):
        return self.get_group_content().filter(groupcontent__pinned=False).exclude(
                article__isnull=False, public=False)

    def get_related_object(self):
        return self.get_group()

    def get_title(self):
        return self.get_group().name


class GroupAvatarUpdate(utils_views.ActionMixin, generic.UpdateView):
    action = 'Avatar ändern'
    fields = ('avatar',)
    layout = ('avatar',)
    menu = 'group'
    model = groups.Group
    permission = 'groups.change_group'

    def get_parent(self):
        return self.object


class GroupLogoUpdate(utils_views.ActionMixin, generic.UpdateView):
    action = 'Logo ändern'
    fields = ('logo',)
    layout = ('logo',)
    menu = 'group'
    model = groups.Group
    permission = 'groups.change_group'

    def get_parent(self):
        return self.object


class GroupMessages(utils_views.List):
    menu = 'group'
    permission = 'content.view_content_list'
    sidebar = []
    template_name = 'content/_thread_list.html'
    title = 'Gespräche'

    def get_queryset(self):
        return self.get_group().get_conversations(self.request.user)

    def get_parent(self):
        return self.get_group()

    def get_related_object(self):
        return self.get_group()


class GroupUpdate(utils_views.ActionMixin, generic.UpdateView):
    action = 'Gruppe ändern'
    fields = ['address', 'closed', 'description', 'date_founded', 'name', 'slug', 'url']
    menu = 'group'
    model = groups.Group
    permission = 'groups.change_group'

    def get_layout(self):
        return (
                'name',
                layout.Field('description', rows=4),
                layout.Field('address', rows=4),
                'url',
                layout.Field('date_founded', data_component='date'),
                bootstrap.PrependedText('slug', '{0}/'.format(
                    sites_models.Site.objects.get_current().domain)),
                'closed',
                ) + super().get_layout()

    def get_parent(self):
        return self.object


class Imprint(utils_views.PageMixin, generic.TemplateView):
    permission = 'entities.view_imprint'
    template_name = 'entities/imprint.html'
    title = 'Impressum'
