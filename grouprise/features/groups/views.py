import django
import django_filters
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, DetailView, TemplateView, UpdateView
from django.views.generic.list import MultipleObjectMixin
from django.urls import reverse
from django_filters.views import FilterView

import grouprise.core
from grouprise.core.views import PermissionMixin, TemplateFilterMixin
from grouprise.features.associations import models as associations
from grouprise.features.content.filters import ContentFilterSet
from grouprise.features.groups import models as groups
from grouprise.features.groups.models import Group
from . import filters, forms, models


class Mixin:
    '''
    Obsolete: Do not use in new code!
    '''
    def get_context_data(self, **kwargs):
        kwargs['group'] = self.get_group()
        return super().get_context_data(**kwargs)

    def get_group(self):
        for attr in ('object', 'related_object'):
            if hasattr(self, attr):
                instance = getattr(self, attr)
                if isinstance(instance, models.Group):
                    return instance
                if hasattr(instance, 'group'):
                    return instance.group
                if hasattr(instance, 'groups'):
                    return instance.groups.first()
        try:
            if 'group_pk' in self.kwargs:
                return models.Group.objects.get(
                        pk=self.kwargs['group_pk'])
            if 'group_slug' in self.kwargs:
                return models.Group.objects.get(
                        slug=self.kwargs['group_slug'])
            if 'group' in self.request.GET:
                return models.Group.objects.get(
                        slug=self.request.GET['group'])
        except models.Group.DoesNotExist:
            pass
        return None


class Create(PermissionMixin, CreateView):
    permission_required = 'groups.create_group'
    model = Group
    fields = ('name',)
    template_name = 'groups/create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.is_authenticated:
            kwargs['instance'] = Group(gestalt_created=self.request.user.gestalt)
        return kwargs


class Detail(PermissionMixin, TemplateFilterMixin, MultipleObjectMixin, DetailView):
    permission_required = 'groups.view'
    model = models.Group
    filterset_class = ContentFilterSet
    paginate_by = 10
    template_name = 'groups/detail.html'

    def get_queryset(self):
        return self.object.associations.ordered_user_content(self.request.user)

    def get_context_data(self, **kwargs):
        associations = self.get_queryset()
        intro_associations = associations.filter(pinned=True).order_by('time_created')
        intro_gallery = intro_associations.filter_galleries().filter(public=True).first()
        if intro_gallery:
            intro_associations = intro_associations.exclude(pk=intro_gallery.pk)
        kwargs['feed_url'] = self.request.build_absolute_uri(
                reverse('group-feed', args=(self.object.pk,)))
        return super().get_context_data(
                associations=associations,
                intro_associations=intro_associations,
                intro_gallery=intro_gallery,
                group=self.object,
                site=get_current_site(self.request),
                **kwargs)

    def get_object(self):
        return self.object


class List(PermissionMixin, FilterView):
    permission_required = 'groups.view_list'
    filterset_class = filters.Group
    paginate_by = 10
    strict = False

    def get_content(self):
        return associations.Association.objects.filter_group_containers().can_view(
                self.request.user)

    def get_queryset(self):
        return groups.Group.objects.order_by('-score')


class Update(PermissionMixin, UpdateView):
    permission_required = 'groups.change'
    model = models.Group
    form_class = forms.Update
    template_name = 'groups/update.html'

    def get_object(self):
        return get_object_or_404(models.Group, slug=self.request.GET.get('group'))


class ImageUpdate(PermissionMixin, UpdateView):
    permission_required = 'groups.change'
    model = models.Group
    fields = ('avatar', 'logo')
    template_name = 'groups/update_images.html'

    def get_object(self):
        return get_object_or_404(models.Group, slug=self.request.GET.get('group'))


class SubscriptionsMemberships(PermissionMixin, TemplateView):
    permission_required = 'groups.change_subscriptions_memberships'
    template_name = 'groups/subscriptions_memberships.html'

    def get_context_data(self, **kwargs):
        kwargs['group'] = self.group
        return super().get_context_data(**kwargs)

    def get_object(self):
        return get_object_or_404(models.Group, slug=self.request.GET.get('group'))

    def get_permission_object(self):
        self.group = super().get_permission_object()
        return self.group
