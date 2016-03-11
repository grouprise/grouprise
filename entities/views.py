from . import forms, models
from content import models as content_models
from crispy_forms import bootstrap, layout
from django.contrib import messages
from django.contrib.auth import mixins as auth_mixins
from django.contrib.sites import shortcuts
from django.core import urlresolvers
from django.views import generic
from django.views.generic import edit as generic_edit_views
from rules.contrib import views as rules_views
from util import views as util_views


class Gestalt(rules_views.PermissionRequiredMixin, generic.DetailView):
    model = models.Gestalt
    permission_required = 'entities.view_gestalt'
    slug_field = 'user__username'

    def get_context_data(self, **kwargs):
        kwargs['content'] = self.object.content_set.permitted(self.request.user)
        return super().get_context_data(**kwargs)


class GestaltUpdate(rules_views.PermissionRequiredMixin, util_views.LayoutMixin, util_views.NavigationMixin, generic.UpdateView):
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


class Group(rules_views.PermissionRequiredMixin, util_views.GestaltMixin, generic.DetailView):
    model = models.Group
    permission_required = 'entities.view_group'

    def get_context_data(self, **kwargs):
        kwargs['blog_content'] = self.get_group_content().filter(groupcontent__pinned=False)
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


class GroupCreate(
        rules_views.PermissionRequiredMixin, 
        util_views.LayoutMixin, 
        util_views.NavigationMixin,
        util_views.SidebarMixin,
        generic.CreateView):
    back_url = urlresolvers.reverse_lazy('index')
    fields = ('name',)
    layout = (
            'name',
            bootstrap.FormActions(layout.Submit('submit', 'Gruppe anlegen')),
            )
    model = models.Group
    permission_required = 'entities.create_group'
    sidebar_template = '_index_sidebar.html'


class GroupMembershipCreate(
        rules_views.PermissionRequiredMixin, 
        util_views.GestaltMixin,
        util_views.GroupMixin,
        util_views.LayoutMixin,
        util_views.NavigationMixin,
        generic.CreateView):
    fields = []
    layout = (bootstrap.FormActions(layout.Submit('submit', 'Mitglied werden')),)
    model = models.Membership
    permission_required = 'entities.create_group_membership'

    def form_valid(self, form):
        group = self.get_group()
        messages.success(self.request, 'Du bist nun Mitglied der Gruppe <em>{}</em>.'.format(group))
        form.instance.gestalt = self.get_gestalt()
        form.instance.group = group
        return super().form_valid(form)

    def get_success_url(self):
        return self.get_group().get_absolute_url()

    def get_permission_object(self):
        return self.get_group()


class GroupMembershipDelete(
        rules_views.PermissionRequiredMixin,
        util_views.NavigationMixin,
        generic.DeleteView):
    model = models.Membership
    permission_required = 'entities.delete_group_membership'

    def get_context_data(self, **kwargs):
        kwargs['group'] = self.object.group
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return self.object.group.get_absolute_url()


class GroupUpdate(
        rules_views.PermissionRequiredMixin, 
        util_views.LayoutMixin, 
        util_views.NavigationMixin, 
        generic.UpdateView):
    fields = ['address', 'date_founded', 'name', 'slug', 'url']
    model = models.Group
    permission_required = 'entities.change_group'

    def get_layout(self):
        DOMAIN = shortcuts.get_current_site(self.request).domain
        return [
                'name',
                layout.Field('address', rows=4),
                'url',
                layout.Field('date_founded', data_provide='datepicker',
                    data_date_language='de', data_date_min_view_mode='months',
                    data_date_start_view='decade'),
                bootstrap.PrependedText('slug', '%(domain)s/' % {'domain': DOMAIN }),
                bootstrap.FormActions(layout.Submit('submit', 'Angaben speichern')),
                ]
