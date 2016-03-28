from . import forms, models
from content import models as content_models
from crispy_forms import bootstrap, layout
from django.contrib import messages
from django.contrib.auth import mixins as auth_mixins
from django.contrib.sites import models as sites_models
from django.core import urlresolvers
from django.views import generic
from rules.contrib import views as rules_views
from util import forms as util_forms, views as util_views

class Gestalt(util_views.PageMixin, generic.DetailView):
    menu = 'gestalt'
    model = models.Gestalt
    permission = 'entities.view_gestalt'
    slug_field = 'user__username'

    def get_context_data(self, **kwargs):
        kwargs['content_list'] = self.object.content_set.permitted(self.request.user)
        return super().get_context_data(**kwargs)

    def get_title(self):
        return str(self.object)

class GestaltUpdate(rules_views.PermissionRequiredMixin, util_views.FormMixin, util_views.NavigationMixin, generic.UpdateView):
    fields = ['about']
    layout = [
            layout.Field('about', rows=5),
            bootstrap.FormActions(layout.Submit('submit', 'Angaben speichern')),
            ]
    model = models.Gestalt
    permission_required = 'entities.change_gestalt'

    def form_invalid(self, form, user_form):
        return self.render_to_response(self.get_context_data(form=form, user_form=user_form))

    def form_valid(self, form, user_form):
        user_form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        if 'user_form' not in kwargs:
            kwargs['user_form'] = self.get_user_form()
        return super().get_context_data(**kwargs)

    def get_form(self):
        form = super().get_form()
        form.helper.form_tag = False
        return form

    def get_user_form(self):
        kwargs = self.get_form_kwargs()
        if 'instance' in kwargs:
            kwargs['instance'] = kwargs['instance'].user
        return forms.User(**kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        user_form = self.get_user_form()
        if form.is_valid() and user_form.is_valid():
            return self.form_valid(form, user_form)
        else:
            return self.form_invalid(form, user_form)

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
        return content_models.Content.objects.permitted(self.request.user).filter(groupcontent__group=self.object)

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
            return models.Membership.objects.get(gestalt=self.get_gestalt(), group=self.object)
        except models.Membership.DoesNotExist:
            return None

    def get_title(self):
        return self.object.name

class GroupCreate(util_views.ActionMixin, generic.CreateView):
    action = 'Gruppe anlegen'
    back_url = 'group-index'
    fields = ('name',)
    layout = ('name',)
    menu = 'group'
    model = models.Group
    permission = 'entities.create_group'

class GroupUpdate(util_views.ActionMixin, generic.UpdateView):
    action = 'Gruppenangaben ändern'
    fields = ['address', 'date_founded', 'name', 'slug', 'url']
    layout = (
            'name',
            layout.Field('address', rows=4),
            'url',
            layout.Field('date_founded', data_provide='datepicker',
                data_date_language='de', data_date_min_view_mode='months',
                data_date_start_view='decade'),
            bootstrap.PrependedText('slug', '%(domain)s/' % {'domain': sites_models.Site.objects.get_current().domain}),
            )
    menu = 'group'
    model = models.Group
    permission = 'entities.change_group'

    def get_parent(self):
        return self.get_group()

class Imprint(util_views.PageMixin, generic.TemplateView):
    parent = 'index'
    permission = 'entities.view_imprint'
    template_name = 'stadt/imprint.html'
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
        form.instance.gestalt = self.get_gestalt()
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
