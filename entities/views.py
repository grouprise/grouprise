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
from utils import forms as utils_forms, views as utils_views

class Gestalt(utils_views.PageMixin, generic.DetailView):
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

class GestaltList(utils_views.List):
    menu = 'gestalt'
    model = models.Gestalt
    parent = 'index'
    permission = 'content.view_content_list'
    sidebar = ('calendar', 'groups')
    title = 'Gestalten'

    def get_context_data(self, **kwargs):
        entities = []
        for entity in self.model.objects.all():
            entities.append((entity, self.get_entity_content(entity).permitted(self.request.user)[:3]))
        kwargs['entities'] = entities
        return super().get_context_data(**kwargs)

    def get_entity_content(self, entity):
        return entity.authored_content

class GestaltUpdate(utils_views.ActionMixin, generic.UpdateView):
    action = 'Profileinstellungen ändern'
    form_class = forms.Gestalt
    menu = 'gestalt'
    message = 'Die Einstellungen wurden geändert.'
    model = models.Gestalt
    permission = 'entities.change_gestalt'

class Group(utils_views.PageMixin, generic.DetailView):
    menu = 'group'
    model = models.Group
    permission = 'entities.view_group'

    def get_context_data(self, **kwargs):
        kwargs['attention'] = self.get_attention()
        kwargs['calendar_events'] = self.get_events().around()
        kwargs['content_list'] = self.get_group_content().filter(groupcontent__pinned=False)
        kwargs['head_gallery'] = self.get_head_gallery()
        kwargs['intro_content'] = self.get_intro_content()
        kwargs['membership'] = self.get_membership()
        kwargs['sidebar_groups'] = models.Group.objects.exclude(pk=self.object.pk).scored().similar(self.object).order_by('-score')
        kwargs['upcoming_events'] = self.get_events().upcoming()
        return super().get_context_data(**kwargs)

    def get_attention(self):
        try:
            return models.GroupAttention.objects.get(attendee=self.request.user.gestalt, group=self.object)
        except (AttributeError, models.GroupAttention.DoesNotExist):
            return None

    def get_events(self):
        return content_models.Event.objects.permitted(self.request.user).filter(groups=self.object)

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

class GroupAttentionCreate(utils_views.ActionMixin, generic.CreateView):
    action = 'Benachrichtigungen erhalten'
    form_class = forms.GroupAttention
    menu = 'group'
    permission = 'entities.create_group_attention'

    def get_initial(self):
        return {'attendee_email': self.request.user.email, 'group': self.get_group().pk}

    def get_parent(self):
        return self.get_group()

    def get_permission_object(self):
        return self.get_group()

class GroupAttentionDelete(utils_views.ActionMixin, utils_views.DeleteView):
    action = 'Keine Benachrichtigungen mehr erhalten'
    layout = layout.HTML('<p>Möchtest Du wirklich keine Benachrichtigungen '
            'für die Gruppe <em>{{ group }}</em> mehr erhalten?</p>')
    menu = 'group'
    model = models.GroupAttention
    permission = 'entities.delete_group_attention'

    def get_parent(self):
        return self.get_group()

class GroupAvatarUpdate(utils_views.ActionMixin, generic.UpdateView):
    action = 'Avatar ändern'
    fields = ('avatar',)
    layout = ('avatar',)
    menu = 'group'
    model = models.Group
    permission = 'entities.change_group'

class GroupCreate(utils_views.ActionMixin, generic.CreateView):
    action = 'Gruppe anlegen'
    back_url = 'group-index'
    fields = ('name',)
    layout = 'name'
    menu = 'group'
    model = models.Group
    permission = 'entities.create_group'

    def get_initial(self):
        if 'name' in self.request.GET:
            return {'name': self.request.GET['name']}

class GroupList(utils_views.List):
    menu = 'group'
    ordering = '-score'
    parent = 'index'
    queryset = models.Group.objects.scored()
    permission = 'content.view_content_list'
    sidebar = ('calendar',)
    title = 'Gruppen'

class GroupLogoUpdate(utils_views.ActionMixin, generic.UpdateView):
    action = 'Logo ändern'
    fields = ('logo',)
    layout = ('logo',)
    menu = 'group'
    model = models.Group
    permission = 'entities.change_group'

class GroupUpdate(utils_views.ActionMixin, generic.UpdateView):
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
                ) + super().get_layout()

class Imprint(utils_views.PageMixin, generic.TemplateView):
    parent = 'index'
    permission = 'entities.view_imprint'
    template_name = 'entities/imprint.html'
    title = 'Impressum'

class MembershipCreate(utils_views.ActionMixin, generic.CreateView):
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

class MembershipDelete(utils_views.ActionMixin, utils_views.DeleteView):
    action = 'Mitgliedschaft beenden'
    layout = layout.HTML('<p>Möchtest Du Deine Mitgliedschaft in der Gruppe '
        '<em>{{ group }}</em> auf {{ site.name }} wirklich beenden?</p>')
    menu = 'group'
    model = models.Membership
    permission = 'entities.delete_membership'

    def get_parent(self):
        return self.get_group()
