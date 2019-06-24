from django.db.models import Q
from django.db.models.functions import Lower
from django.urls import reverse
from django.views.generic import FormView, ListView
from taggit.models import Tag

from grouprise.core.views import PermissionMixin
from grouprise.features.associations import models as associations
from grouprise.features.groups.models import Group
from . import forms


class Detail(PermissionMixin, ListView):
    permission_required = 'tags.view'
    model = associations.Association
    paginate_by = 10
    template_name = 'tags/detail.html'

    def get_queryset(self):
        self.tag = self.get_tag()
        self.groups = Group.objects.filter(tags__in=[self.tag])
        tagged_content_query = Q(content__tags__in=[self.tag])
        tagged_group_content_query = (
                Q(entity_type=Group.content_type) & Q(entity_id__in=self.groups))
        return super().get_queryset().ordered_user_content(self.request.user) \
            .filter(tagged_content_query | tagged_group_content_query)

    def get_tag(self):
        try:
            return Tag.objects.get(slug=self.kwargs.get('slug'))
        except Tag.DoesNotExist:
            return Tag(name=self.kwargs.get('slug'), slug=self.kwargs.get('slug'))


class TagGroup(PermissionMixin, FormView):
    permission_required = 'tags.tag_group'
    form_class = forms.TagGroup
    template_name = 'tags/tag_group.html'

    def form_valid(self, form):
        group = form.cleaned_data['group']
        group.tags.add(self.tag)
        return super().form_valid(form)

    def get_form_kwargs(self):
        self.tag = self.get_tag()
        kwargs = super().get_form_kwargs()
        kwargs['group_queryset'] = self.request.user.gestalt.groups.exclude(
                tags__in=[self.tag]).order_by(Lower('name'))
        return kwargs

    def get_permission_object(self):
        return None

    def get_success_url(self):
        return reverse('tag', args=(self.tag.slug,))

    def get_tag(self):
        slug = self.kwargs.get('slug')
        tag, _ = Tag.objects.get_or_create(slug=slug, defaults={'name': slug})
        return tag
