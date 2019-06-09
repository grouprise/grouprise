import re

from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.urls import reverse
from django.views.generic import CreateView, DetailView, TemplateView, UpdateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormView
from django.views.generic.list import MultipleObjectMixin
from django_filters.views import FilterView

from grouprise.core.views import PermissionMixin, TemplateFilterMixin
from grouprise.features.associations import models as associations
from grouprise.features.content.filters import ContentFilterSet
from grouprise.features.groups import filters, forms, models
from grouprise.features.groups.forms import RecommendForm
from grouprise.features.groups.models import Group
from grouprise.features.groups.notifications import RecommendNotification


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
        return models.Group.objects.order_by('-score')


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


class RecommendView(PermissionMixin, SingleObjectMixin, SuccessMessageMixin, FormView):
    model = Group
    slug_url_kwarg = 'group'
    permission_required = 'groups.recommend'
    form_class = RecommendForm
    template_name = 'groups/recommend.html'
    success_message = 'Die Empfehlungen wurden versendet.'

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        return super().post(*args, **kwargs)

    def get_initial(self):
        context = dict(
            group=self.object,
            site=Site.objects.get_current(),
            user=self.request.user
        )
        template = get_template('groups/recommend.txt')
        return dict(text=template.render(context).strip())

    def form_valid(self, form):
        recipients = self.get_recipients(form.cleaned_data['recipients'])
        self.send_recommendations(recipients, form.cleaned_data['text'])
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_recipients(self, data: str) -> list:
        email_pattern = re.compile(
                r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}', flags=re.IGNORECASE)
        gestalt_pattern = re.compile(r'@([\w-]+)')

        # get a list of usernames
        data_without_emails = email_pattern.sub('', data)
        gestalten = gestalt_pattern.findall(data_without_emails)

        # recipients are the explicitly given email addresses + the email addresses of the
        # users given by username (@gestalt syntax)
        # non-existing users are silently ignored
        recipients = email_pattern.findall(data)
        for username in gestalten:
            try:
                recipients.append(User.objects.get(username=username).email)
            except User.DoesNotExist:
                pass
        return recipients

    def send_recommendations(self, recipients: list, text: str) -> None:
        for recipient in recipients:
            RecommendNotification(text).send(recipient)
