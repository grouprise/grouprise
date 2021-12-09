import django
from django import db, http, shortcuts, urls
from django.contrib.messages import info, success
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, DeleteView, FormView

import grouprise.core
from grouprise.core.models import PermissionToken
from grouprise.core.views import PermissionMixin
from grouprise.features.associations import models as associations
from grouprise.features.contributions import models as contributions
from grouprise.features.gestalten import models as gestalten_models
from grouprise.features.gestalten import views as gestalten_views
from grouprise.features.gestalten.models import Gestalt
from grouprise.features.groups import models as groups_models
from grouprise.features.groups.models import Group
from grouprise.features.memberships.forms import CreateMembershipForm
from grouprise.features.memberships.models import Membership

from . import forms, models, notifications


class Apply(grouprise.core.views.PermissionMixin, django.views.generic.CreateView):
    permission_required = "memberships.apply"
    form_class = forms.Apply
    template_name = "memberships/apply.html"

    def get_form_kwargs(self):
        contribution = contributions.Contribution()
        contribution.author = self.request.user.gestalt
        contribution.container = self.association.container
        kwargs = super().get_form_kwargs()
        kwargs["contribution"] = contribution
        kwargs["instance"] = models.Application(group=self.association.entity)
        return kwargs

    def get_permission_object(self):
        self.association = django.shortcuts.get_object_or_404(
            associations.Association, pk=self.kwargs.get("association_pk")
        )
        return self.association.entity

    def get_success_url(self):
        return self.association.get_absolute_url()


class AcceptApplication(
    grouprise.core.views.PermissionMixin, django.views.generic.CreateView
):
    permission_required = "memberships.accept_application"
    model = models.Membership
    fields = []
    template_name = "memberships/accept.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = models.Membership(
            created_by=self.request.user.gestalt,
            group=self.application.group,
            member=self.application.contribution.author,
        )
        return kwargs

    def get_permission_object(self):
        self.application = django.shortcuts.get_object_or_404(
            models.Application, pk=self.kwargs.get("application_pk")
        )
        return self.application

    def get_success_url(self):
        try:
            return associations.Association.objects.get(
                group=self.application.group,
                container_type=self.application.contribution.container.content_type,
                container_id=self.application.contribution.container.id,
            ).get_absolute_url()
        except associations.Association.DoesNotExist:
            return self.application.group.get_absolute_url()


class Join(PermissionMixin, SuccessMessageMixin, CreateView):
    permission_required = "memberships.join"
    model = models.Membership
    fields = []
    template_name = "memberships/join.html"
    success_message = "Du bist nun Mitglied der Gruppe."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.model(
            created_by=self.gestalt, group=self.group, member=self.gestalt
        )
        return kwargs

    def get_permission_object(self):
        self.gestalt = (
            self.request.user.gestalt if self.request.user.is_authenticated else None
        )
        self.group = get_object_or_404(Group, slug=self.kwargs.get("group"))
        return self.group

    def get_success_url(self):
        return self.group.get_absolute_url()

    def handle_no_permission(self):
        if (
            self.gestalt
            and self.gestalt.user.is_authenticated
            and self.group.members.filter(pk=self.gestalt.pk).exists()
        ):
            django.contrib.messages.info(
                self.request, "Du bist bereits Mitglied der Gruppe."
            )
            return django.http.HttpResponseRedirect(self.group.get_absolute_url())
        else:
            return super().handle_no_permission()


class JoinConfirm(Join):
    def form_valid(self, form):
        self.token.delete()
        return super().form_valid(form)

    def get_permission_object(self):
        self.token = get_object_or_404(
            PermissionToken,
            feature_key="group-join",
            secret_key=self.kwargs.get("secret_key"),
        )
        self.gestalt = self.token.gestalt
        self.group = self.token.target
        return self.group

    def has_permission(self):
        obj = self.get_permission_object()
        perms = self.get_permission_required()
        return self.gestalt.user.has_perms(perms, obj)


class JoinRequest(PermissionMixin, FormView):
    permission_required = "memberships.join_request"
    form_class = forms.Request
    template_name = "memberships/join_request.html"

    def form_valid(self, form):
        gestalt = Gestalt.objects.get_or_create_by_email(form.cleaned_data["member"])
        notification = notifications.Join(self.group)
        notification.token = PermissionToken.objects.create(
            gestalt=gestalt, target=self.group, feature_key="group-join"
        )
        notification.send(gestalt)
        info(self.request, "Es wurde eine E-Mail an die angebene Adresse versendet.")
        return super().form_valid(form)

    def get_permission_object(self):
        self.group = get_object_or_404(Group, slug=self.kwargs.get("group_slug"))
        return self.group

    def get_success_url(self):
        return self.group.get_absolute_url()


class Members(gestalten_views.List):
    permission_required = "memberships.view_list"
    template_name = "memberships/list.html"

    def get_permission_object(self):
        self.group = shortcuts.get_object_or_404(
            groups_models.Group, pk=self.kwargs["group_pk"]
        )
        return self.group

    def get_queryset(self):
        return gestalten_models.Gestalt.objects.filter(
            memberships__group=self.group
        ).order_by("-score")


class MemberAdd(PermissionMixin, CreateView):
    permission_required = "memberships.create_membership"
    form_class = CreateMembershipForm
    template_name = "memberships/create.html"

    def get_form_kwargs(self):
        membership = Membership(created_by=self.request.user.gestalt, group=self.group)
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = membership
        return kwargs

    def get_permission_object(self):
        self.group = get_object_or_404(Group, pk=self.kwargs["group_pk"])
        return self.group

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except db.IntegrityError:
            info(self.request, "Die Gestalt ist bereits Mitglied.")
            return http.HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return urls.reverse("members", args=(self.group.pk,))


class Resign(PermissionMixin, DeleteView):
    permission_required = "memberships.delete"
    template_name = "memberships/delete.html"

    def delete(self, *args, **kwargs):
        success(self.request, "Du bist nicht mehr Mitglied dieser Gruppe.")
        return super().delete(*args, **kwargs)

    def get_object(self):
        return self.gestalt.memberships.filter(group=self.group)

    def get_permission_object(self):
        self.gestalt = (
            self.request.user.gestalt if self.request.user.is_authenticated else None
        )
        self.group = get_object_or_404(Group, pk=self.kwargs.get("group_pk"))
        return self.group

    def get_success_url(self):
        return self.group.get_absolute_url()


class ResignConfirm(Resign):
    def delete(self, *args, **kwargs):
        self.token.delete()
        return super().delete(*args, **kwargs)

    def get_permission_object(self):
        self.token = get_object_or_404(
            PermissionToken,
            feature_key="group-resign",
            secret_key=self.kwargs.get("secret_key"),
        )
        self.gestalt = self.token.gestalt
        self.group = self.token.target
        return self.group

    def has_permission(self):
        obj = self.get_permission_object()
        perms = self.get_permission_required()
        return self.gestalt.user.has_perms(perms, obj)


class ResignRequest(PermissionMixin, FormView):
    permission_required = "memberships.delete_request"
    form_class = forms.Request
    template_name = "memberships/delete_request.html"

    def form_valid(self, form):
        email = form.cleaned_data["member"]
        try:
            member = self.group.members.get_by_email(email)
            notification = notifications.Resign(self.group)
            notification.token = PermissionToken.objects.create(
                gestalt=member, target=self.group, feature_key="group-resign"
            )
            notification.send(member)
        except Gestalt.DoesNotExist:
            notifications.NoMember(self.group).send(email)
        info(self.request, "Es wurde eine E-Mail an die angebene Adresse versendet.")
        return super().form_valid(form)

    def get_permission_object(self):
        self.group = get_object_or_404(Group, pk=self.kwargs.get("group_pk"))
        return self.group

    def get_success_url(self):
        return self.group.get_absolute_url()
