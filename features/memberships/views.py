import django
from django import db, http, shortcuts
from django.contrib import messages
from django import urls

import core
from core import fields, views
from features.associations import models as associations
from features.contributions import models as contributions
from features.gestalten import models as gestalten_models, views as gestalten_views
from features.groups import models as groups_models, views as groups_views
from core import views as utils_views
from . import forms, models


class Apply(core.views.PermissionMixin, django.views.generic.CreateView):
    permission_required = 'memberships.apply'
    form_class = forms.Apply
    template_name = 'memberships/apply.html'

    def get_form_kwargs(self):
        contribution = contributions.Contribution()
        contribution.author = self.request.user.gestalt
        contribution.container = self.association.container
        kwargs = super().get_form_kwargs()
        kwargs['contribution'] = contribution
        kwargs['instance'] = models.Application(group=self.association.entity)
        return kwargs

    def get_permission_object(self):
        self.association = django.shortcuts.get_object_or_404(
                associations.Association, pk=self.kwargs.get('association_pk'))
        return self.association.entity

    def get_success_url(self):
        return self.association.get_absolute_url()


class AcceptApplication(core.views.PermissionMixin, django.views.generic.CreateView):
    permission_required = 'memberships.accept_application'
    model = models.Membership
    fields = []
    template_name = 'memberships/accept.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = models.Membership(
                created_by=self.request.user.gestalt, group=self.application.group,
                member=self.application.contribution.author)
        return kwargs

    def get_permission_object(self):
        self.application = django.shortcuts.get_object_or_404(
                models.Application, pk=self.kwargs.get('application_pk'))
        return self.application

    def get_success_url(self):
        try:
            return associations.Association.objects.get(
                    group=self.application.group,
                    container_type=self.application.contribution.container.content_type,
                    container_id=self.application.contribution.container.id
                    ).get_absolute_url()
        except associations.Association.DoesNotExist:
            return self.application.group.get_absolute_url()


class MembershipMixin(groups_views.Mixin):
    model = models.Membership
    title = 'Mitgliedschaft'

    def get_related_object(self):
        return self.get_group()


class Join(MembershipMixin, views.Create):
    action = 'Beitreten *'
    data_field_classes = (
            fields.current_gestalt('created_by'),
            fields.related_object('group'),
            fields.current_gestalt('member'))
    description = (
            'Der Gruppe <em>{{ group }}</em> auf {{ site.name }} beitreten *')
    permission_required = 'memberships.join_group'
    template_name = 'memberships/join.html'

    def handle_no_permission(self):
        if self.request.user.is_authenticated() and self.related_object.members.filter(
                pk=self.request.user.gestalt.pk).exists():
            django.contrib.messages.info(self.request, 'Du bist bereits Mitglied der Gruppe.')
            return django.http.HttpResponseRedirect(self.related_object.get_absolute_url())
        else:
            return super().handle_no_permission()


class Members(gestalten_views.List):
    permission_required = 'memberships.view_list'
    template_name = 'memberships/list.html'

    def get_permission_object(self):
        self.group = shortcuts.get_object_or_404(
                groups_models.Group, pk=self.kwargs['group_pk'])
        return self.group

    def get_queryset(self):
        return gestalten_models.Gestalt.objects.filter(
                memberships__group=self.group).order_by('-score')


class MemberAdd(MembershipMixin, views.Create):
    action = 'Mitglied aufnehmen'
    data_field_classes = (
            fields.current_gestalt('created_by'),
            fields.related_object('group'),
            fields.email_gestalt('member'))
    permission_required = 'memberships.create_membership'

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except db.IntegrityError:
            messages.info(
                    self.request, 'Die Gestalt ist bereits Mitglied.')
            return http.HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return urlresolvers.reverse('members', args=(self.related_object.pk,))


class Resign(MembershipMixin, utils_views.Delete):
    action = 'Austreten'
    description = 'Aus der Gruppe <em>{{ group }}</em> austreten'
    permission_required = 'memberships.delete_membership'

    def get_object(self):
        return models.Membership.objects.filter(
                group=self.related_object,
                member=self.request.user.gestalt
                ).first()
