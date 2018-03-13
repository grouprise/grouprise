import django.urls
import django.views.generic
from django import shortcuts
from django.contrib.contenttypes import models as contenttypes
from django.views import generic

import core.views
import features
from core.views import base
from features.associations import models as associations
from features.associations.views import get_association_or_404
from features.contributions import view_mixins as contributions
from features.files import forms as files
from features.galleries import forms as galleries
from features.gestalten import models as gestalten
from features.groups import models as groups
from . import forms


class List(core.views.PermissionMixin, django.views.generic.ListView):
    permission_required = 'content.list'
    model = associations.Association
    paginate_by = 10
    template_name = 'content/list.html'

    def get_queryset(self):
        return super().get_queryset().ordered_user_content(self.request.user)


class DetailBase(features.associations.views.AssociationMixin,
                 contributions.ContributionFormMixin, base.PermissionMixin, generic.DetailView):
    permission_required = 'content.view'
    permission_required_post = 'content.comment'
    model = associations.Association
    template_name = 'articles/detail.html'

    form_class = features.contributions.forms.Text

    def get_object(self, queryset=None):
        return self.get_association()

    def get_template_names(self):
        if self.object.container.is_poll:
            names = ('polls/detail.html',)
        elif self.object.container.is_gallery:
            names = ('galleries/detail.html',)
        elif self.object.container.is_file:
            names = ('files/detail.html',)
        elif self.object.container.is_event:
            names = ('events/detail.html',)
        else:
            names = super().get_template_names()
        return names


class Detail(DetailBase):
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.container.is_poll:
            return features.polls.views.Detail(kwargs=kwargs, request=request).get(
                    request, *args, **kwargs)
        return super().get(request, *args, **kwargs)


class Permalink(django.views.generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        association = get_association_or_404(pk=kwargs.get('association_pk'))
        return django.urls.reverse(
                'content', args=(association.entity.slug, association.slug))


class Create(base.PermissionMixin, generic.CreateView):
    permission_required = 'content.create'
    model = associations.Association
    form_class = forms.Create
    template_name = 'content/create.html'
    with_time = False

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['author'] = self.request.user.gestalt
        kwargs['instance'] = associations.Association(entity=self.entity)
        kwargs['with_time'] = self.with_time
        return kwargs

    def get_initial(self):
        return {'public': True}

    def get_permission_object(self):
        if 'entity_slug' in self.kwargs:
            self.entity = shortcuts.get_object_or_404(
                    groups.Group, slug=self.kwargs['entity_slug'])
        elif self.request.user.is_authenticated:
            self.entity = self.request.user.gestalt
        else:
            self.entity = None
        return self.entity

    def has_permission(self):
        has_perm = super().has_permission()
        if has_perm and self.entity and self.entity.is_group:
            has_perm = self.request.user.has_perm('content.group_create', self.entity)
        return has_perm


class Update(base.PermissionMixin, generic.UpdateView):
    permission_required = 'content.change'
    model = associations.Association
    form_class = forms.Update

    def get_form_class(self):
        if self.object.container.is_poll:
            form_class = features.polls.forms.Update
        elif self.object.container.is_gallery:
            form_class = galleries.Update
        elif self.object.container.is_file:
            form_class = files.Update
        else:
            form_class = self.form_class
        return form_class

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['author'] = self.request.user.gestalt
        return kwargs

    def get_initial(self):
        return {
                'title': self.object.container.title,
                'image': self.object.container.image,
                'text': self.object.container.versions.last().text,
                'place': self.object.container.place,
                'time': self.object.container.time,
                'until_time': self.object.container.until_time,
                'all_day': self.object.container.all_day,
                }

    def get_object(self):
        try:
            self.entity = groups.Group.objects.get(slug=self.kwargs['entity_slug'])
        except groups.Group.DoesNotExist:
            self.entity = shortcuts.get_object_or_404(
                    gestalten.Gestalt, user__username=self.kwargs['entity_slug'])
        return shortcuts.get_object_or_404(
                associations.Association,
                entity_id=self.entity.id,
                entity_type=contenttypes.ContentType.objects.get_for_model(self.entity),
                slug=self.kwargs['association_slug'])

    def get_template_names(self):
        if self.object.container.is_poll:
            name = 'polls/update.html'
        elif self.object.container.is_gallery:
            name = 'galleries/update.html'
        elif self.object.container.is_file:
            name = 'files/update.html'
        elif self.object.container.is_event:
            name = 'events/update.html'
        else:
            name = 'articles/update.html'
        return [name]
