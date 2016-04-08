from . import forms, models
from content import models as content_models
from crispy_forms import bootstrap, layout
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import mixins as auth_mixins
from django.contrib.sites import models as sites_models
from django.core import urlresolvers
from django.db import models as django_models
from django.views import generic
from rules.contrib import views as rules_views
from utils import forms as util_forms, views as util_views

class BaseEntityList(util_views.PageMixin, generic.ListView):
    parent = 'index'
    permission = 'content.view_content_list'

    def get_context_data(self, **kwargs):
        entities = []
        for entity in self.model.objects.all():
            entities.append((entity, self.get_entity_content(entity).permitted(self.request.user)[:settings.LATEST_ENTITY_CONTENT_PREVIEW_COUNT]))
        kwargs['entities'] = entities
        return super().get_context_data(**kwargs)

class Gestalt(util_views.PageMixin, generic.DetailView):
    menu = 'gestalt'
    model = models.Gestalt
    permission = 'entities.view_gestalt'
    sidebar = ('calendar',)
    slug_field = 'user__username'

    def get_context_data(self, **kwargs):
        kwargs['content_list'] = content_models.Content.objects.permitted(self.request.user).filter(django_models.Q(gestaltcontent__gestalt=self.object) | django_models.Q(author=self.object))
        return super().get_context_data(**kwargs)

    def get_title(self):
        return str(self.object)

class GestaltList(BaseEntityList):
    menu = 'gestalt'
    model = models.Gestalt
    sidebar = ('calendar', 'groups')
    title = 'Gestalten'

    def get_entity_content(self, entity):
        return entity.authored_content

class GestaltUpdate(util_views.ActionMixin, generic.UpdateView):
    action = 'Profileinstellungen ändern'
    form_class = forms.Gestalt
    menu = 'gestalt'
    message = 'Die Einstellungen wurden geändert.'
    model = models.Gestalt
    permission = 'entities.change_gestalt'

class Group(util_views.PageMixin, generic.DetailView):
    menu = 'group'
    model = models.Group
    permission = 'entities.view_group'

    def get_context_data(self, **kwargs):
        kwargs['content_list'] = self.get_group_content().filter(groupcontent__pinned=False)
        kwargs['head_gallery'] = self.get_head_gallery()
        kwargs['intro_content'] = self.get_intro_content()
        kwargs['membership'] = self.get_membership()
        return super().get_context_data(**kwargs)

    def get_group_content(self):
        return self.object.content.permitted(self.request.user)

    def get_head_gallery(self):
        return self.get_group_content().filter(gallery__isnull=False, groupcontent__pinned=True).first()

    def get_intro_content(self):
        pinned_content = self.get_group_content().filter(groupcontent__pinned=True)
        try:
            return pinned_content.exclude(pk=self.get_head_gallery().pk)
        except AttributeError:
            return pinned_content

    def get_membership(self):
        try:
            return models.Membership.objects.get(gestalt=self.request.user.gestalt, group=self.object)
        except (AttributeError, models.Membership.DoesNotExist):
            return None

    def get_title(self):
        return self.object.name

class GroupCreate(util_views.ActionMixin, generic.CreateView):
    action = 'Gruppe anlegen'
    back_url = 'group-index'
    fields = ('name',)
    layout = 'name'
    menu = 'group'
    model = models.Group
    permission = 'entities.create_group'

class GroupList(BaseEntityList):
    menu = 'group'
    model = models.Group
    sidebar = ('calendar',)
    title = 'Gruppen'

    def get_entity_content(self, entity):
        return entity.content

class GroupUpdate(util_views.ActionMixin, generic.UpdateView):
    action = 'Gruppenangaben ändern'
    fields = ['address', 'date_founded', 'name', 'slug', 'url']
    menu = 'group'
    model = models.Group
    permission = 'entities.change_group'

    def get_layout(self):
        return (
                'name',
                layout.Field('address', rows=4),
                'url',
                layout.Field('date_founded', data_provide='datepicker',
                    data_date_language='de', data_date_min_view_mode='months',
                    data_date_start_view='decade'),
                bootstrap.PrependedText('slug', '%(domain)s/' % {'domain': sites_models.Site.objects.get_current().domain}),
                )

class Imprint(util_views.PageMixin, generic.TemplateView):
    parent = 'index'
    permission = 'entities.view_imprint'
    template_name = 'entities/imprint.html'
    title = 'Impressum'

class MembershipCreate(util_views.ActionMixin, generic.CreateView):
    action = 'Mitglied werden'
    fields = []
    layout = layout.HTML('<p>Möchtest Du Mitglied der Gruppe '
            '<em>{{ group }}</em> auf {{ site.name }} werden?</p>'
            '<p>Falls Du in der <em>echten Welt</em> noch nicht Mitglied in '
            'der Gruppe bist und es werden möchtest, sprich bitte die anderen '
            'Gruppenmitglieder an.</p>')
    menu = 'group'
    model = models.Membership
    permission = 'entities.create_membership'

    def form_valid(self, form):
        group = self.get_group()
        messages.success(self.request, 'Du bist nun Mitglied der Gruppe <em>{}</em>.'.format(group))
        form.instance.gestalt = self.request.user.gestalt
        form.instance.group = group
        return super().form_valid(form)

    def get_parent(self):
        return self.get_group()

    def get_permission_object(self):
        return self.get_group()

class MembershipDelete(util_views.ActionMixin, util_views.DeleteView):
    action = 'Mitgliedschaft beenden'
    layout = layout.HTML('<p>Möchtest Du Deine Mitgliedschaft in der Gruppe '
        '<em>{{ group }}</em> auf {{ site.name }} wirklich beenden?</p>')
    menu = 'group'
    model = models.Membership
    permission = 'entities.delete_membership'

    def get_parent(self):
        return self.get_group()
